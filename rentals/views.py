from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from .models import Rental
from cars.models import Car
from .serializers import RentalSerializer, StartRentalSerializer, EndRentalSerializer
from .strategy import (
    DefaultPriceStrategy, SubscriptionPriceStrategy,
    PromotionPriceStrategy, CombinedDiscountStrategy, LicenseCategoryStrategy
)
from .command import StartRentalCommand, EndRentalCommand, RentalCommandInvoker
from .decorators import RentalServiceFactory
from core.singleton import PricingService
from core.observer import RentalEventManager, EmailNotifier, SMSNotifier


class StartRentalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartRentalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.is_verified:
            return Response({'error': 'пользователь не верифицирован'}, status=status.HTTP_403_FORBIDDEN)

        try:
            car = Car.objects.get(id=serializer.validated_data['car_id'])
        except Car.DoesNotExist:
            return Response({'error': 'автомобиль не найден'}, status=status.HTTP_404_NOT_FOUND)

        if car.status != 'available':
            return Response({'error': 'автомобиль недоступен'}, status=status.HTTP_400_BAD_REQUEST)

        if user.license_category != car.required_license:
            return Response({
                'error': f'для аренды этого авто нужна категория прав {car.get_required_license_display()}'
            }, status=status.HTTP_403_FORBIDDEN)

        services = serializer.validated_data.get('services', [])

        rental, rental_service = Rental.create_rental(user, car, services)

        command = StartRentalCommand(rental.id, car, user)
        invoker = RentalCommandInvoker()
        invoker.execute_command(command)

        pricing_service = PricingService()
        pricing_service.register_strategy('default', DefaultPriceStrategy())
        pricing_service.register_strategy('subscription', SubscriptionPriceStrategy(10))
        pricing_service.register_strategy('license_a', LicenseCategoryStrategy('A'))
        pricing_service.register_strategy('license_b', LicenseCategoryStrategy('B'))
        pricing_service.register_strategy('license_c', LicenseCategoryStrategy('C'))

        base_price_per_minute = float(car.price_per_minute)

        strategy_name = f'license_{user.license_category.lower()}'
        price_per_minute = pricing_service.calculate_price(1, strategy_name, base_price_per_minute)

        rental.total_price = Decimal(str(rental_service.get_price()))
        rental.save()

        event_manager = RentalEventManager()
        event_manager.attach(EmailNotifier())
        event_manager.attach(SMSNotifier())
        event_manager.trigger_rental_started(user, car, rental)

        return Response({
            'rental_id': rental.id,
            'message': 'аренда успешно начата',
            'services': rental_service.get_description(),
            'price_per_minute': float(price_per_minute),
            'total_with_services': float(rental.total_price)
        }, status=status.HTTP_201_CREATED)


class EndRentalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EndRentalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            rental = Rental.objects.get(id=serializer.validated_data['rental_id'])
        except Rental.DoesNotExist:
            return Response({'error': 'аренда не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if rental.user != request.user and request.user.role != 'admin':
            return Response({'error': 'нет доступа к этой аренде'}, status=status.HTTP_403_FORBIDDEN)

        if rental.status != 'active':
            return Response({'error': 'аренда уже завершена'}, status=status.HTTP_400_BAD_REQUEST)

        invoker = RentalCommandInvoker()
        command = EndRentalCommand(rental, rental.car, None)
        final_price = command.execute()

        from cars.models import Location
        end_location = Location.objects.create(
            city="Москва",
            street="Конечная",
            house_number="1",
            latitude=serializer.validated_data['end_latitude'],
            longitude=serializer.validated_data['end_longitude']
        )
        rental.end_location = end_location
        rental.save()

        event_manager = RentalEventManager()
        event_manager.attach(EmailNotifier())
        event_manager.attach(SMSNotifier())
        event_manager.trigger_rental_ended(rental.user, rental, final_price or 0)

        duration_minutes = (timezone.now() - rental.start_time).total_seconds() / 60

        return Response({
            'rental_id': rental.id,
            'duration_minutes': round(duration_minutes, 2),
            'total_price': float(final_price) if final_price else 0,
            'message': 'аренда завершена'
        }, status=status.HTTP_200_OK)


class RentalHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rentals = Rental.objects.filter(user=request.user).order_by('-start_time')
        serializer = RentalSerializer(rentals, many=True)
        return Response(serializer.data)


class RentalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, rental_id):
        try:
            rental = Rental.objects.get(id=rental_id)
            if rental.user != request.user and request.user.role != 'admin':
                return Response({'error': 'нет доступа к этой аренде'},
                                status=status.HTTP_403_FORBIDDEN)
            serializer = RentalSerializer(rental)
            return Response(serializer.data)
        except Rental.DoesNotExist:
            return Response({'error': 'аренда не найдена'},
                            status=status.HTTP_404_NOT_FOUND)


class PricingDemoView(APIView):
    def post(self, request):
        minutes = request.data.get('minutes', 60)
        base_price_per_minute = request.data.get('base_price', 10)

        strategies = {
            'default': DefaultPriceStrategy(),
            'subscription_10': SubscriptionPriceStrategy(10),
            'subscription_20': SubscriptionPriceStrategy(20),
            'promotion_15': PromotionPriceStrategy(15),
            'promotion_25': PromotionPriceStrategy(25),
            'combined': CombinedDiscountStrategy(10, 15),
            'license_a': LicenseCategoryStrategy('A'),
            'license_b': LicenseCategoryStrategy('B'),
            'license_c': LicenseCategoryStrategy('C')
        }

        results = {}
        for name, strategy in strategies.items():
            results[name] = strategy.calculate(minutes, base_price_per_minute)

        return Response({
            'minutes': minutes,
            'base_price_per_minute': base_price_per_minute,
            'base_total': minutes * base_price_per_minute,
            'strategies': results
        })
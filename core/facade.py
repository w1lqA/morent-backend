from django.utils import timezone
from decimal import Decimal
from rentals.models import Rental
from cars.models import Car
from rentals.command import StartRentalCommand, EndRentalCommand, RentalCommandInvoker
from core.singleton import PricingService
from core.observer import RentalEventManager, EmailNotifier, SMSNotifier
from rentals.strategy import DefaultPriceStrategy, SubscriptionPriceStrategy, LicenseCategoryStrategy


class RentalFacade:
    def __init__(self):
        self._pricing_service = PricingService()
        self._event_manager = RentalEventManager()
        self._command_invoker = RentalCommandInvoker()
        self._init_services()

    def _init_services(self):
        self._pricing_service.register_strategy('default', DefaultPriceStrategy())
        self._pricing_service.register_strategy('subscription', SubscriptionPriceStrategy(10))
        self._pricing_service.register_strategy('license_a', LicenseCategoryStrategy('A'))
        self._pricing_service.register_strategy('license_b', LicenseCategoryStrategy('B'))
        self._pricing_service.register_strategy('license_c', LicenseCategoryStrategy('C'))

        self._event_manager.attach(EmailNotifier())
        self._event_manager.attach(SMSNotifier())

    def start_rental(self, user, car_id, services=None):
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return {'success': False, 'error': 'автомобиль не найден'}

        if car.status != 'available':
            return {'success': False, 'error': 'автомобиль недоступен'}

        if not user.is_verified:
            return {'success': False, 'error': 'пользователь не верифицирован'}

        if user.license_category != car.required_license:
            return {
                'success': False,
                'error': f'для аренды этого авто нужна категория прав {car.get_required_license_display()}'
            }

        rental, rental_service = Rental.create_rental(user, car, services or [])

        command = StartRentalCommand(rental.id, car, user)
        self._command_invoker.execute_command(command)

        base_price_per_minute = float(car.price_per_minute)
        strategy_name = f'license_{user.license_category.lower()}'
        price_per_minute = self._pricing_service.calculate_price(1, strategy_name, base_price_per_minute)

        rental.total_price = Decimal(str(rental_service.get_price()))
        rental.save()

        self._event_manager.trigger_rental_started(user, car, rental)

        return {
            'success': True,
            'rental_id': rental.id,
            'services': rental_service.get_description(),
            'price_per_minute': float(price_per_minute),
            'total_with_services': float(rental.total_price)
        }

    def end_rental(self, user, rental_id, end_latitude, end_longitude):
        try:
            rental = Rental.objects.get(id=rental_id)
        except Rental.DoesNotExist:
            return {'success': False, 'error': 'аренда не найдена'}

        if rental.user != user and user.role != 'admin':
            return {'success': False, 'error': 'нет доступа к этой аренде'}

        if rental.status != 'active':
            return {'success': False, 'error': 'аренда уже завершена'}

        command = EndRentalCommand(rental, rental.car, None)
        final_price = self._command_invoker.execute_command(command)

        from cars.models import Location
        end_location = Location.objects.create(
            city="москва",
            street="конечная",
            house_number="1",
            latitude=end_latitude,
            longitude=end_longitude
        )
        rental.end_location = end_location
        rental.save()

        self._event_manager.trigger_rental_ended(user, rental, final_price or 0)

        duration_minutes = (timezone.now() - rental.start_time).total_seconds() / 60

        return {
            'success': True,
            'rental_id': rental.id,
            'duration_minutes': round(duration_minutes, 2),
            'total_price': float(final_price) if final_price else 0
        }

    def undo_last_rental_action(self):
        return self._command_invoker.undo_last()

    def attach_observer(self, observer):
        self._event_manager.attach(observer)

    def detach_observer(self, observer):
        self._event_manager.detach(observer)

    def get_observers(self):
        return self._event_manager.get_observers()
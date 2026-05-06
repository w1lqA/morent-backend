from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .services import NearestCarFinder
from .serializers import NearestCarSerializer, CarListSerializer, CarDetailSerializer
from .models import Car
from core.proxy import CarServiceProxy

class NearestCarsView(APIView):
    def post(self, request):
        serializer = NearestCarSerializer(data=request.data)
        if serializer.is_valid():
            user_lat = serializer.validated_data['latitude']
            user_lon = serializer.validated_data['longitude']
            limit = serializer.validated_data['limit']

            real_service = NearestCarFinder()
            proxy_service = CarServiceProxy(real_service)

            nearest_cars = proxy_service.find_nearest_cars(user_lat, user_lon, limit)

            return Response({
                'count': len(nearest_cars),
                'cars': nearest_cars
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarListView(APIView):
    def get(self, request):
        cars = Car.objects.filter(status='available')

        # фильтрация по тегам
        tag = request.query_params.get('tag')
        if tag:
            cars = cars.filter(tags__name=tag)

        # фильтрация по вместимости
        min_capacity = request.query_params.get('min_capacity')
        max_capacity = request.query_params.get('max_capacity')
        if min_capacity:
            cars = cars.filter(capacity__gte=min_capacity)
        if max_capacity:
            cars = cars.filter(capacity__lte=max_capacity)

        # фильтрация по цене
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            cars = cars.filter(price_per_minute__gte=min_price)
        if max_price:
            cars = cars.filter(price_per_minute__lte=max_price)

        # фильтрация по коробке передач
        steering = request.query_params.get('steering')
        if steering:
            cars = cars.filter(steering=steering)

        # пагинация
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        paginator = Paginator(cars, page_size)
        page_obj = paginator.get_page(page)

        serializer = CarListSerializer(page_obj, many=True)

        return Response({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': int(page),
            'page_size': int(page_size),
            'results': serializer.data
        })

class CarDetailView(APIView):
    def get(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
            serializer = CarDetailSerializer(car)
            return Response(serializer.data)
        except Car.DoesNotExist:
            return Response({'error': 'автомобиль не найден'},
                            status=status.HTTP_404_NOT_FOUND)

class CarCategoriesView(APIView):
    def get(self, request):
        from cars.composite_iterator import CarCategory, CarLeaf, CarFleet

        fleet = CarFleet("Автопарк Morent")

        economy = CarCategory("Эконом-класс")
        for car in Car.objects.filter(price_per_minute__lt=6)[:5]:
            economy.add(CarLeaf(car))

        comfort = CarCategory("Комфорт-класс")
        for car in Car.objects.filter(price_per_minute__gte=6, price_per_minute__lt=12)[:5]:
            comfort.add(CarLeaf(car))

        business = CarCategory("Бизнес-класс")
        for car in Car.objects.filter(price_per_minute__gte=12)[:5]:
            business.add(CarLeaf(car))

        fleet.add_category(economy)
        fleet.add_category(comfort)
        fleet.add_category(business)

        result = {
            'fleet_name': fleet.name,
            'total_cars': fleet.get_count(),
            'average_price': fleet.get_price(),
            'categories': []
        }

        for cat in fleet._categories:
            category_data = {
                'name': cat.name,
                'car_count': cat.get_count(),
                'average_price': cat.get_price(),
                'cars': []
            }
            for child in cat._children:
                if hasattr(child, 'car'):
                    category_data['cars'].append({
                        'brand': child.car.brand,
                        'model': child.car.model,
                        'price_per_minute': float(child.car.price_per_minute)
                    })
            result['categories'].append(category_data)

        return Response(result)


class CarIteratorView(APIView):
    def get(self, request):
        cars = list(Car.objects.filter(status='available'))

        from cars.composite_iterator import CarIterator, CarFilterIterator

        iterator = CarIterator(cars)

        def is_electric(car):
            return 'electric' in [tag.name for tag in car.tags.all()]

        electric_cars = [car for car in cars if is_electric(car)]
        electric_iterator = CarFilterIterator(electric_cars, is_electric)

        all_cars_list = []
        for car in iterator:
            all_cars_list.append(f"{car.brand} {car.model} (ID: {car.id})")

        electric_cars_list = []
        for car in electric_iterator:
            electric_cars_list.append(f"{car.brand} {car.model}")

        result = {
            'total_cars': len(cars),
            'first_car': None,
            'last_car': None,
            'all_cars': all_cars_list,
            'electric_cars': electric_cars_list
        }

        if cars:
            first = cars[0]
            last = cars[-1]
            result['first_car'] = f"{first.brand} {first.model}"
            result['last_car'] = f"{last.brand} {last.model}"

        return Response(result)
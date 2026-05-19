from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .services import NearestCarFinder
from .serializers import NearestCarSerializer, CarListSerializer, CarDetailSerializer
from .models import Car
from core.proxy import CarServiceProxy
from core.facade import RentalFacade
from cars.adapter import CategoryAdapter, InternalCategoryService, LicenseCategoryAdapter


class NearestCarsView(APIView):
    def post(self, request):
        serializer = NearestCarSerializer(data=request.data)
        if serializer.is_valid():
            user_lat = serializer.validated_data['latitude']
            user_lon = serializer.validated_data['longitude']
            limit = serializer.validated_data['limit']
            radius = serializer.validated_data.get('radius')

            real_service = NearestCarFinder()
            proxy_service = CarServiceProxy(real_service)

            if radius:
                nearest_cars = proxy_service.find_nearest_cars(user_lat, user_lon, limit, radius)
            else:
                nearest_cars = proxy_service.find_nearest_cars(user_lat, user_lon, limit)

            return Response({
                'count': len(nearest_cars),
                'cars': nearest_cars
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarsInRadiusView(APIView):
    def post(self, request):
        serializer = NearestCarSerializer(data=request.data)
        if serializer.is_valid():
            user_lat = serializer.validated_data['latitude']
            user_lon = serializer.validated_data['longitude']
            radius = serializer.validated_data.get('radius', 5)

            cars_in_radius = NearestCarFinder.find_cars_in_radius(user_lat, user_lon, radius)

            return Response({
                'radius_km': radius,
                'count': len(cars_in_radius),
                'cars': cars_in_radius
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryAdapterView(APIView):
    def get(self, request):
        internal_service = InternalCategoryService()
        adapter = CategoryAdapter(internal_service)
        categories = adapter.get_categories()
        return Response({'categories': categories})


class LicenseCategoryAdapterView(APIView):
    def get(self, request):
        adapter = LicenseCategoryAdapter()
        categories = adapter.get_categories()
        return Response({'license_categories': categories})

    def post(self, request):
        category_name = request.data.get('category')
        if not category_name:
            return Response({'error': 'укажите category'}, status=status.HTTP_400_BAD_REQUEST)

        adapter = LicenseCategoryAdapter()
        cars = adapter.get_cars_by_category(category_name)
        return Response({'category': category_name, 'cars': cars})


class CarListView(APIView):
    def get(self, request):
        cars = Car.objects.filter(status='available')

        tag = request.query_params.get('tag')
        if tag:
            cars = cars.filter(tags__name=tag)

        min_capacity = request.query_params.get('min_capacity')
        max_capacity = request.query_params.get('max_capacity')
        if min_capacity:
            cars = cars.filter(capacity__gte=min_capacity)
        if max_capacity:
            cars = cars.filter(capacity__lte=max_capacity)

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            cars = cars.filter(price_per_minute__gte=min_price)
        if max_price:
            cars = cars.filter(price_per_minute__lte=max_price)

        steering = request.query_params.get('steering')
        if steering:
            cars = cars.filter(steering=steering)

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

        fleet = CarFleet("автопарк morent")

        economy = CarCategory("эконом-класс")
        for car in Car.objects.filter(price_per_minute__lt=6)[:5]:
            economy.add(CarLeaf(car))

        comfort = CarCategory("комфорт-класс")
        for car in Car.objects.filter(price_per_minute__gte=6, price_per_minute__lt=12)[:5]:
            comfort.add(CarLeaf(car))

        business = CarCategory("бизнес-класс")
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
        from cars.composite_iterator import CarCollection, CarIterator, CarFilterIterator

        cars = list(Car.objects.filter(status='available'))
        collection = CarCollection(cars)
        iterator = CarIterator(collection)

        def is_electric(car):
            return 'electric' in [tag.name for tag in car.tags.all()]

        electric_cars = [car for car in cars if is_electric(car)]
        electric_collection = CarCollection(electric_cars)
        electric_iterator = CarFilterIterator(electric_collection, is_electric)

        all_cars_list = []
        for car in iterator:
            all_cars_list.append(f"{car.brand} {car.model} (ID: {car.id})")

        electric_cars_list = []
        for car in electric_iterator:
            electric_cars_list.append(f"{car.brand} {car.model}")

        result = {
            'total_cars': collection.size(),
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


class RentalFacadeView(APIView):
    def post(self, request):
        action = request.data.get('action')

        if action == 'start':
            facade = RentalFacade()
            result = facade.start_rental(
                user=request.user,
                car_id=request.data.get('car_id'),
                services=request.data.get('services', [])
            )
            return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

        elif action == 'end':
            facade = RentalFacade()
            result = facade.end_rental(
                user=request.user,
                rental_id=request.data.get('rental_id'),
                end_latitude=request.data.get('end_latitude'),
                end_longitude=request.data.get('end_longitude')
            )
            return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

        elif action == 'undo':
            facade = RentalFacade()
            result = facade.undo_last_rental_action()
            return Response({'undo_success': result})

        return Response({'error': 'неизвестное действие'}, status=status.HTTP_400_BAD_REQUEST)
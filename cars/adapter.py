from abc import ABC, abstractmethod


class CategoryTarget(ABC):
    @abstractmethod
    def get_categories(self):
        pass

    @abstractmethod
    def get_cars_by_category(self, category_name):
        pass


class InternalCategoryService:
    def get_all_categories(self):
        from cars.models import Car
        categories_data = {}
        cars = Car.objects.filter(status='available')

        for car in cars:
            price = float(car.price_per_minute)
            if price < 6:
                cat = 'economy'
            elif price < 12:
                cat = 'comfort'
            else:
                cat = 'business'

            if cat not in categories_data:
                categories_data[cat] = []
            categories_data[cat].append({
                'id': car.id,
                'brand': car.brand,
                'model': car.model,
                'price_per_minute': price
            })
        return categories_data

    def get_cars_by_price_range(self, min_price, max_price):
        from cars.models import Car
        return Car.objects.filter(
            status='available',
            price_per_minute__gte=min_price,
            price_per_minute__lte=max_price
        )


class CategoryAdapter(CategoryTarget):
    def __init__(self, internal_service):
        self._internal_service = internal_service

    def get_categories(self):
        internal_data = self._internal_service.get_all_categories()
        return [
            {'name': name, 'count': len(cars), 'cars': cars}
            for name, cars in internal_data.items()
        ]

    def get_cars_by_category(self, category_name):
        price_ranges = {
            'economy': (0, 5.99),
            'comfort': (6, 11.99),
            'business': (12, 999),
            'sport': (15, 999),
            'family': (8, 20)
        }

        if category_name not in price_ranges:
            return []

        min_price, max_price = price_ranges[category_name]
        cars = self._internal_service.get_cars_by_price_range(min_price, max_price)

        return [
            {
                'id': car.id,
                'brand': car.brand,
                'model': car.model,
                'price_per_minute': float(car.price_per_minute),
                'required_license': car.get_required_license_display()
            }
            for car in cars
        ]


class LicenseCategoryAdapter(CategoryTarget):
    def __init__(self):
        self._license_map = {
            'A': ['мотоциклы', 'скутеры'],
            'B': ['легковые', 'седаны', 'хэтчбеки', 'кроссоверы'],
            'C': ['грузовые', 'фургоны', 'микроавтобусы']
        }

    def get_categories(self):
        return [{'name': k, 'vehicle_types': v} for k, v in self._license_map.items()]

    def get_cars_by_category(self, category_name):
        from cars.models import Car
        from users.models import LicenseCategory

        if category_name.upper() not in [c.value for c in LicenseCategory]:
            return []

        cars = Car.objects.filter(status='available', required_license=category_name.upper())
        return [
            {
                'id': car.id,
                'brand': car.brand,
                'model': car.model,
                'price_per_minute': float(car.price_per_minute)
            }
            for car in cars
        ]
import math
from .models import Car, CarStatus


class NearestCarFinder:

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)

    @classmethod
    def find_nearest_cars(cls, user_lat, user_lon, limit=10, radius=None):
        available_cars = Car.objects.filter(
            status=CarStatus.AVAILABLE
        ).select_related('location')

        results = []
        for car in available_cars:
            if not car.location:
                continue

            distance = cls.calculate_distance(
                user_lat, user_lon,
                float(car.location.latitude),
                float(car.location.longitude)
            )

            if radius is not None and distance > radius:
                continue

            results.append({
                'id': car.id,
                'brand': car.brand,
                'model': car.model,
                'year': car.year,
                'plate_number': car.plate_number,
                'price_per_minute': float(car.price_per_minute),
                'distance': round(distance, 6),
                'location': {
                    'city': car.location.city,
                    'street': car.location.street,
                    'house_number': car.location.house_number,
                    'latitude': float(car.location.latitude),
                    'longitude': float(car.location.longitude)
                }
            })

        results.sort(key=lambda x: x['distance'])
        return results[:limit]

    @classmethod
    def find_cars_in_radius(cls, user_lat, user_lon, radius_km=5):
        return cls.find_nearest_cars(user_lat, user_lon, limit=100, radius=radius_km)

    @classmethod
    def get_nearest_car(cls, user_lat, user_lon):
        nearest = cls.find_nearest_cars(user_lat, user_lon, limit=1)
        return nearest[0] if nearest else None
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


class CarFactory(ABC):
    """абстрактная фабрика для создания автомобилей"""

    @abstractmethod
    def create_car(self, **kwargs):
        pass

    @abstractmethod
    def create_location(self, **kwargs):
        pass


class EconomyCarFactory(CarFactory):
    """фабрика эконом-класса"""

    def create_car(self, brand="Kia", model="Rio", year=2023, plate_number=None, price_per_minute=5.0, **kwargs):
        from cars.models import Car
        return Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate_number or f"ECO{datetime.now().timestamp()}",
            price_per_minute=Decimal(price_per_minute),
            **kwargs
        )

    def create_location(self, city="Москва", street="Экономная", house_number="1", latitude=55.75, longitude=37.61):
        from cars.models import Location
        return Location.objects.create(
            city=city,
            street=street,
            house_number=house_number,
            latitude=latitude,
            longitude=longitude
        )


class BusinessCarFactory(CarFactory):
    """фабрика бизнес-класса"""

    def create_car(self, brand="Mercedes", model="E-Class", year=2024, plate_number=None, price_per_minute=15.0,
                   **kwargs):
        from cars.models import Car
        return Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate_number or f"BIZ{datetime.now().timestamp()}",
            price_per_minute=Decimal(price_per_minute),
            **kwargs
        )

    def create_location(self, city="Москва", street="Престижная", house_number="10", latitude=55.76, longitude=37.62):
        from cars.models import Location
        return Location.objects.create(
            city=city,
            street=street,
            house_number=house_number,
            latitude=latitude,
            longitude=longitude
        )


class SportCarFactory(CarFactory):
    """фабрика спорт-класса"""

    def create_car(self, brand="Ferrari", model="488", year=2024, plate_number=None, price_per_minute=30.0, **kwargs):
        from cars.models import Car
        return Car.objects.create(
            brand=brand,
            model=model,
            year=year,
            plate_number=plate_number or f"SPT{datetime.now().timestamp()}",
            price_per_minute=Decimal(price_per_minute),
            **kwargs
        )

    def create_location(self, city="Москва", street="Спортивная", house_number="5", latitude=55.77, longitude=37.63):
        from cars.models import Location
        return Location.objects.create(
            city=city,
            street=street,
            house_number=house_number,
            latitude=latitude,
            longitude=longitude
        )


class RentalFactory(ABC):
    """абстрактная фабрика для создания аренды"""

    @abstractmethod
    def create_rental(self, user, car, start_time=None, **kwargs):
        pass


class StandardRentalFactory(RentalFactory):
    """стандартная фабрика аренды"""

    def create_rental(self, user, car, start_time=None, **kwargs):
        from rentals.models import Rental
        if not start_time:
            start_time = timezone.now()

        return Rental.objects.create(
            user=user,
            car=car,
            start_time=start_time,
            status='active',
            **kwargs
        )


class UserFactory(ABC):
    """абстрактная фабрика для создания пользователей"""

    @abstractmethod
    def create_user(self, email, phone, **kwargs):
        pass


class VerifiedUserFactory(UserFactory):
    """фабрика верифицированных пользователей"""

    def create_user(self, email, phone, **kwargs):
        from users.models import User, VerificationStatus, Role

        return User.objects.create_user(
            email=email,
            phone=phone,
            first_name=kwargs.get('first_name', 'Verified'),
            last_name=kwargs.get('last_name', 'User'),
            password=kwargs.get('password', 'verified123'),
            role=Role.USER,
            verification_status=VerificationStatus.VERIFIED,
            is_verified=True,
            passport_series=kwargs.get('passport_series', '1234'),
            passport_number=kwargs.get('passport_number', '567890'),
            driving_license_number=kwargs.get('driving_license_number', 'DL123456'),
            **kwargs
        )


class UnverifiedUserFactory(UserFactory):
    """фабрика неверифицированных пользователей"""

    def create_user(self, email, phone, **kwargs):
        from users.models import User, VerificationStatus, Role

        return User.objects.create_user(
            email=email,
            phone=phone,
            first_name=kwargs.get('first_name', 'Unverified'),
            last_name=kwargs.get('last_name', 'User'),
            password=kwargs.get('password', 'unverified123'),
            role=Role.USER,
            verification_status=VerificationStatus.PENDING,
            is_verified=False,
            **kwargs
        )


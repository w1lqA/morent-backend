from abc import ABC, abstractmethod


class RentalService(ABC):
    """Базовый интерфейс для аренды"""

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_description(self):
        pass


class BaseRental(RentalService):
    """Базовый объект аренды"""

    def __init__(self, rental, base_price):
        self.rental = rental
        self._base_price = base_price

    def get_price(self):
        return self._base_price

    def get_description(self):
        return f"Аренда #{self.rental.id}"


class InsuranceDecorator(RentalService):
    """Декоратор для страховки"""

    def __init__(self, rental_service):
        self._rental_service = rental_service
        self._insurance_price = 200  # 200 руб

    def get_price(self):
        return self._rental_service.get_price() + self._insurance_price

    def get_description(self):
        return f"{self._rental_service.get_description()} + Страховка"


class ChildSeatDecorator(RentalService):
    """Декоратор для детского кресла"""

    def __init__(self, rental_service):
        self._rental_service = rental_service
        self._child_seat_price = 150  # 150 руб

    def get_price(self):
        return self._rental_service.get_price() + self._child_seat_price

    def get_description(self):
        return f"{self._rental_service.get_description()} + Детское кресло"


class AdditionalDriverDecorator(RentalService):
    """Декоратор для дополнительного водителя"""

    def __init__(self, rental_service):
        self._rental_service = rental_service
        self._additional_driver_price = 300  # 300 руб

    def get_price(self):
        return self._rental_service.get_price() + self._additional_driver_price

    def get_description(self):
        return f"{self._rental_service.get_description()} + Доп. водитель"


class GPSDecorator(RentalService):
    """Декоратор для GPS-навигатора"""

    def __init__(self, rental_service):
        self._rental_service = rental_service
        self._gps_price = 100  # 100 руб

    def get_price(self):
        return self._rental_service.get_price() + self._gps_price

    def get_description(self):
        return f"{self._rental_service.get_description()} + GPS"


# Фабрика для создания декорированных услуг
class RentalServiceFactory:
    """Создает аренду с дополнительными услугами"""

    @staticmethod
    def create_rental_with_services(rental, base_price, services=None):
        service = BaseRental(rental, base_price)

        if services:
            service_map = {
                'insurance': InsuranceDecorator,
                'child_seat': ChildSeatDecorator,
                'additional_driver': AdditionalDriverDecorator,
                'gps': GPSDecorator
            }

            for service_name in services:
                if service_name in service_map:
                    service = service_map[service_name](service)

        return service
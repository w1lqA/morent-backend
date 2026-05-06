from abc import ABC, abstractmethod


class CarState(ABC):
    """Абстрактный класс состояния автомобиля"""

    @abstractmethod
    def rent(self, car):
        pass

    @abstractmethod
    def return_car(self, car):
        pass

    @abstractmethod
    def maintain(self, car):
        pass

    @abstractmethod
    def get_status(self):
        pass


class AvailableState(CarState):
    """Состояние: автомобиль доступен для аренды"""

    def rent(self, car):
        print(f"🚗 Автомобиль {car.brand} {car.model} арендован")
        from .models import CarStatus
        car.status = CarStatus.RENTED
        car.save()
        car.set_state(RentedState())
        return True

    def return_car(self, car):
        print(f"❌ Нельзя вернуть автомобиль, который не арендован")
        return False

    def maintain(self, car):
        from .models import CarStatus
        car.status = CarStatus.MAINTENANCE
        car.save()
        car.set_state(MaintenanceState())
        return True

    def get_status(self):
        return "Доступен"


class RentedState(CarState):
    """Состояние: автомобиль в аренде"""

    def rent(self, car):
        print(f"❌ Автомобиль уже в аренде")
        return False

    def return_car(self, car):
        print(f"✅ Автомобиль {car.brand} {car.model} возвращен")
        from .models import CarStatus
        car.status = CarStatus.AVAILABLE
        car.save()
        car.set_state(AvailableState())
        return True

    def maintain(self, car):
        print(f"❌ Нельзя отправить на обслуживание автомобиль в аренде")
        return False

    def get_status(self):
        return "Арендован"


class MaintenanceState(CarState):
    """Состояние: автомобиль на обслуживании"""

    def rent(self, car):
        print(f"❌ Нельзя арендовать автомобиль на обслуживании")
        return False

    def return_car(self, car):
        print(f"❌ Нельзя вернуть автомобиль на обслуживании")
        return False

    def maintain(self, car):
        print(f"✅ Автомобиль {car.brand} {car.model} прошел обслуживание")
        from .models import CarStatus
        car.status = CarStatus.AVAILABLE
        car.save()
        car.set_state(AvailableState())
        return True

    def get_status(self):
        return "На обслуживании"
from abc import ABC, abstractmethod


class RentalProcess(ABC):
    """Шаблонный метод для процесса аренды"""

    def process_rental(self, user, car, minutes, promotion_code=None):
        """Шаблонный метод: определяет последовательность шагов"""
        if not self.validate_user(user):
            return {"success": False, "message": "Пользователь не верифицирован"}

        if not self.validate_car(car):
            return {"success": False, "message": "Автомобиль недоступен"}

        price = self.calculate_price(car, minutes, promotion_code)

        rental = self.create_rental(user, car, minutes, price)

        self.update_car_status(car)

        self.notify_user(user, rental, price)

        return {
            "success": True,
            "rental_id": rental.id,
            "price": price,
            "message": "Аренда успешно оформлена"
        }

    @abstractmethod
    def validate_user(self, user):
        """Проверка пользователя"""
        pass

    @abstractmethod
    def validate_car(self, car):
        """Проверка автомобиля"""
        pass

    @abstractmethod
    def calculate_price(self, car, minutes, promotion_code):
        """Расчет стоимости"""
        pass

    @abstractmethod
    def create_rental(self, user, car, minutes, price):
        """Создание записи аренды"""
        pass

    @abstractmethod
    def update_car_status(self, car):
        """Обновление статуса авто"""
        pass

    @abstractmethod
    def notify_user(self, user, rental, price):
        """Уведомление пользователя"""
        pass


class StandardRentalProcess(RentalProcess):
    """Конкретная реализация шаблонного метода"""

    def validate_user(self, user):
        return user.is_verified and user.verification_status == 'verified'

    def validate_car(self, car):
        return car.status == 'available'

    def calculate_price(self, car, minutes, promotion_code):
        base_price = minutes * float(car.price_per_minute)
        # Здесь можно добавить логику скидок
        return base_price

    def create_rental(self, user, car, minutes, price):
        from .models import Rental
        from django.utils import timezone

        rental = Rental.objects.create(
            user=user,
            car=car,
            start_time=timezone.now(),
            total_price=price,
            status='active'
        )
        return rental

    def update_car_status(self, car):
        car.status = 'rented'
        car.save()

    def notify_user(self, user, rental, price):
        print(f"📧 Уведомление отправлено на {user.email}: Аренда #{rental.id} на сумму {price}")
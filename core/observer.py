from abc import ABC, abstractmethod


class Observer(ABC):
    """Интерфейс наблюдателя"""

    @abstractmethod
    def update(self, event_type, data):
        pass


class Subject:
    """Субъект, за которым наблюдают"""

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event_type, data):
        for observer in self._observers:
            observer.update(event_type, data)


class EmailNotifier(Observer):
    """Наблюдатель для Email уведомлений"""

    def update(self, event_type, data):
        if event_type == 'rental_started':
            print(f"📧 Письмо пользователю {data['user_email']}: Аренда начата")
        elif event_type == 'rental_ended':
            print(f"📧 Письмо пользователю {data['user_email']}: Аренда завершена. Сумма: {data['price']}")


class SMSNotifier(Observer):
    """Наблюдатель для SMS уведомлений"""

    def update(self, event_type, data):
        if event_type == 'rental_started':
            print(f"📱 SMS на {data['user_phone']}: Код доступа к авто {data['car_plate']}")
        elif event_type == 'car_returned':
            print(f"📱 SMS на {data['user_phone']}: Автомобиль возвращен")


class AdminNotifier(Observer):
    """Наблюдатель для администраторов"""

    def update(self, event_type, data):
        if event_type == 'user_verified':
            print(f"👨‍💼 Админ: Пользователь {data['user_email']} прошел верификацию")
        elif event_type == 'issue_reported':
            print(f"⚠️ Админ: Проблема с авто {data['car_id']}")


class RentalEventManager(Subject):
    """Менеджер событий аренды"""

    def trigger_rental_started(self, user, car, rental):
        self.notify('rental_started', {
            'user_email': user.email,
            'user_phone': user.phone,
            'car_plate': car.plate_number,
            'rental_id': rental.id
        })

    def trigger_rental_ended(self, user, rental, price):
        self.notify('rental_ended', {
            'user_email': user.email,
            'rental_id': rental.id,
            'price': price
        })
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, event_type, data):
        pass


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def get_observers(self):
        return self._observers.copy()

    def notify(self, event_type, data):
        for observer in self._observers:
            observer.update(event_type, data)


class EmailNotifier(Observer):
    def update(self, event_type, data):
        if event_type == 'rental_started':
            print(f"email пользователю {data['user_email']}: аренда начата")
        elif event_type == 'rental_ended':
            print(f"email пользователю {data['user_email']}: аренда завершена. сумма: {data['price']}")


class SMSNotifier(Observer):
    def update(self, event_type, data):
        if event_type == 'rental_started':
            print(f"sms на {data['user_phone']}: код доступа к авто {data['car_plate']}")
        elif event_type == 'car_returned':
            print(f"sms на {data['user_phone']}: автомобиль возвращен")


class AdminNotifier(Observer):
    def update(self, event_type, data):
        if event_type == 'user_verified':
            print(f"админ: пользователь {data['user_email']} прошел верификацию")
        elif event_type == 'issue_reported':
            print(f"админ: проблема с авто {data['car_id']}")


class RentalEventManager(Subject):
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
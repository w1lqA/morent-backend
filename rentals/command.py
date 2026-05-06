from abc import ABC, abstractmethod
from django.utils import timezone
from .models import Rental, RentalStatus


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class StartRentalCommand(Command):
    def __init__(self, rental_id, car, user):
        self.rental_id = rental_id
        self.car = car
        self.user = user
        self.executed = False

    def execute(self):
        if not self.executed:
            self.car.rent()
            self.executed = True
            return True
        return False

    def undo(self):
        if self.executed:
            self.car.return_car()
            self.executed = False
            return True
        return False


class EndRentalCommand(Command):
    def __init__(self, rental, car, price_calculator):
        self.rental = rental
        self.car = car
        self.price_calculator = price_calculator
        self.calculated_price = None
        self.executed = False

    def execute(self):
        if not self.executed:
            minutes = (timezone.now() - self.rental.start_time).total_seconds() / 60
            self.calculated_price = minutes * float(self.car.price_per_minute)
            self.rental.end_time = timezone.now()
            self.rental.total_price = self.calculated_price
            self.rental.status = RentalStatus.FINISHED
            self.rental.save()
            self.car.return_car()
            self.executed = True
            return self.calculated_price
        return None

    def undo(self):
        if self.executed:
            self.rental.end_time = None
            self.rental.total_price = 0
            self.rental.status = RentalStatus.ACTIVE
            self.rental.save()
            self.executed = False
            return True
        return False


class RentalCommandInvoker:
    def __init__(self):
        self._history = []

    def execute_command(self, command):
        result = command.execute()
        self._history.append(command)
        return result

    def undo_last(self):
        if self._history:
            command = self._history.pop()
            return command.undo()
        return False
from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


def validate_year(value):
    from datetime import datetime
    current_year = datetime.now().year
    if value < 1990 or value > current_year + 1:
        raise ValidationError(f'год выпуска должен быть между 1990 и {current_year + 1}')


def validate_price(value):
    if value <= 0:
        raise ValidationError('цена за минуту должна быть больше 0')


def validate_plate_number(value):
    if len(value) < 6 or len(value) > 9:
        raise ValidationError('номер должен содержать 6-9 символов')


class Location(models.Model):
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=7,
                                   validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=10, decimal_places=7,
                                    validators=[MinValueValidator(-180), MaxValueValidator(180)])

    def __str__(self):
        return f"{self.city}, {self.street} {self.house_number}"


class CarStatus(models.TextChoices):
    AVAILABLE = 'available', 'Доступен'
    RENTED = 'rented', 'Арендован'
    MAINTENANCE = 'maintenance', 'На обслуживании'


class SteeringType(models.TextChoices):
    MANUAL = 'manual', 'Механическая'
    AUTOMATIC = 'automatic', 'Автоматическая'
    ELECTRIC = 'electric', 'Электрическая'


class CarTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(validators=[validate_year])
    plate_number = models.CharField(max_length=20, unique=True, validators=[validate_plate_number])
    status = models.CharField(max_length=20, choices=CarStatus.choices, default=CarStatus.AVAILABLE)
    price_per_minute = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price])
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(CarTag, through='CarTagMap')

    # новые поля
    capacity = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(50)])
    steering = models.CharField(max_length=20, choices=SteeringType.choices, default=SteeringType.AUTOMATIC)
    gasoline = models.CharField(max_length=20, default="50L")
    description = models.TextField(blank=True, null=True)

    _car_state = None

    def _init_state(self):
        from .state import AvailableState, RentedState, MaintenanceState
        if self.status == CarStatus.AVAILABLE:
            self._car_state = AvailableState()
        elif self.status == CarStatus.RENTED:
            self._car_state = RentedState()
        elif self.status == CarStatus.MAINTENANCE:
            self._car_state = MaintenanceState()

    def set_state(self, state):
        self._car_state = state

    def rent(self):
        if self._car_state:
            return self._car_state.rent(self)
        return False

    def return_car(self):
        if self._car_state:
            return self._car_state.return_car(self)
        return False

    def maintain(self):
        if self._car_state:
            return self._car_state.maintain(self)
        return False

    def get_state_status(self):
        if self._car_state:
            return self._car_state.get_status()
        return "неизвестно"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/%Y/%m/%d/')
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.car.brand} {self.car.model} - {self.order}"


class CarTagMap(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    tag = models.ForeignKey(CarTag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('car', 'tag')


@receiver(post_init, sender=Car)
def initialize_car_state(sender, instance, **kwargs):
    instance._init_state()
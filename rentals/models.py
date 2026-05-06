from django.db import models
from django.conf import settings
from cars.models import Car, Location
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

def validate_price(value):
    if value < 0:
        raise ValidationError('цена не может быть отрицательной')

class RentalStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    FINISHED = 'finished', 'Завершена'
    CANCELLED = 'cancelled', 'Отменена'

class Rental(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    start_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='rentals_start')
    end_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='rentals_end')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[validate_price])
    status = models.CharField(max_length=20, choices=RentalStatus.choices, default=RentalStatus.ACTIVE)

    def clean(self):
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError('время завершения не может быть раньше времени начала')

    def __str__(self):
        return f"аренда #{self.id} - {self.user.email} - {self.car}"
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_discount(value):
    if value < 0 or value > 100:
        raise ValidationError('скидка должна быть от 0 до 100 процентов')

class Subscription(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percent = models.IntegerField(default=0, validators=[validate_discount])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError('дата окончания должна быть позже даты начала')

    def __str__(self):
        return f"{self.user.email} - {self.subscription.name}"

class Promotion(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    discount_percent = models.IntegerField(validators=[validate_discount])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError('дата окончания должна быть позже даты начала')

    def __str__(self):
        return self.title

class InsuranceType(models.TextChoices):
    BASIC = 'basic', 'базовая'
    FULL = 'full', 'полная'
    CASCO = 'casco', 'каско'

class Insurance(models.Model):
    rental = models.ForeignKey('rentals.Rental', on_delete=models.CASCADE, related_name='insurances')
    insurance_type = models.CharField(max_length=10, choices=InsuranceType.choices, default=InsuranceType.BASIC)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"страховка {self.get_insurance_type_display()} для аренды {self.rental.id}"
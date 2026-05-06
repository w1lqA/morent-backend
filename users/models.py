from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError

class Role(models.TextChoices):
    USER = 'user', 'Пользователь'
    ADMIN = 'admin', 'Администратор'
    MODERATOR = 'moderator', 'Модератор'


class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'На проверке'
    VERIFIED = 'verified', 'Верифицирован'
    REJECTED = 'rejected', 'Отклонен'


class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        if not phone:
            raise ValueError('Телефон обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.ADMIN)
        extra_fields.setdefault('verification_status', VerificationStatus.VERIFIED)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(email, phone, password, **extra_fields)


def validate_passport_series(value):
    if len(str(value)) != 4:
        raise ValidationError('серия паспорта должна содержать 4 символа')


def validate_passport_number(value):
    if len(str(value)) != 6:
        raise ValidationError('номер паспорта должен содержать 6 символов')


def validate_driving_license_number(value):
    if len(str(value)) < 10 or len(str(value)) > 12:
        raise ValidationError('номер водительского удостоверения должен содержать 10-12 символов')


class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)

    passport_series = models.CharField(max_length=4, blank=True, null=True)
    passport_number = models.CharField(max_length=6, blank=True, null=True)
    passport_issued_by = models.CharField(max_length=255, blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)

    driving_license_number = models.CharField(max_length=20, blank=True, null=True)
    driving_license_category = models.CharField(max_length=10, blank=True, null=True)
    driving_license_expiry_date = models.DateField(blank=True, null=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    @property
    def is_verified(self):
        return self.verification_status == VerificationStatus.VERIFIED

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
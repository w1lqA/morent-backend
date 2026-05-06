from django.core.cache import cache
from cars.services import NearestCarFinder
import hashlib
import json


class CarServiceProxy:
    """Proxy для кеширования результатов поиска автомобилей"""

    def __init__(self, real_service):
        self._real_service = real_service
        self._cache_timeout = 60  # 60 секунд кеширования

    def _get_cache_key(self, user_lat, user_lon, limit):
        key_data = f"{user_lat}:{user_lon}:{limit}"
        return f"nearest_cars_{hashlib.md5(key_data.encode()).hexdigest()}"

    def find_nearest_cars(self, user_lat, user_lon, limit=10):
        # Проверяем кеш
        cache_key = self._get_cache_key(user_lat, user_lon, limit)
        cached_result = cache.get(cache_key)

        if cached_result:
            print(f"📦 [PROXY] Возвращаем из кеша: {len(cached_result)} автомобилей")
            return cached_result

        # Если нет в кеше, вызываем реальный сервис
        print(f"🔍 [PROXY] Кеша нет, ищем реальные данные")
        result = self._real_service.find_nearest_cars(user_lat, user_lon, limit)

        # Сохраняем в кеш
        cache.set(cache_key, result, self._cache_timeout)

        return result

    def clear_cache(self):
        cache.clear()
        print("🗑️ [PROXY] Кеш очищен")


class AdminAccessProxy:
    """Proxy для контроля доступа администратора"""

    def __init__(self, user):
        self._user = user
        self._real_service = None

    def _check_admin_access(self):
        from users.models import Role

        if not self._user or self._user.role != Role.ADMIN:
            raise PermissionError("Доступ запрещен. Требуются права администратора.")
        return True

    def get_all_rentals(self):
        if self._check_admin_access():
            from rentals.models import Rental
            return Rental.objects.all()

    def get_all_users(self):
        if self._check_admin_access():
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.all()

    def update_car_status(self, car_id, new_status):
        if self._check_admin_access():
            from cars.models import Car
            car = Car.objects.get(id=car_id)
            car.status = new_status
            car.save()
            return car


class ImageProxy:
    """Proxy для ленивой загрузки изображений (экономия памяти)"""

    def __init__(self, image_url):
        self._image_url = image_url
        self._image = None

    def display(self):
        if not self._image:
            print(f"🖼️ [PROXY] Загружаем изображение: {self._image_url}")
            self._image = self._load_image()
        print(f"🖼️ [PROXY] Отображаем изображение")
        return self._image

    def _load_image(self):
        # Здесь реальная загрузка изображения
        return f"Loaded: {self._image_url}"
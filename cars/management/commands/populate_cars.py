from django.core.management.base import BaseCommand
from cars.models import Car, Location, CarTag, CarStatus, CarImage, SteeringType
from users.models import User, Role, VerificationStatus
from promotions.models import Subscription, UserSubscription
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'наполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write("начинаем наполнение базы данных...")

        # 1. создаем локации
        self.stdout.write("создаем локации...")
        locations = [
            Location.objects.create(
                city="Москва", street="Тверская", house_number="1",
                latitude=55.757, longitude=37.615
            ),
            Location.objects.create(
                city="Москва", street="Арбат", house_number="10",
                latitude=55.751, longitude=37.590
            ),
            Location.objects.create(
                city="Москва", street="Кутузовский", house_number="20",
                latitude=55.742, longitude=37.540
            ),
            Location.objects.create(
                city="Москва", street="Ленинский", house_number="15",
                latitude=55.701, longitude=37.580
            ),
            Location.objects.create(
                city="Москва", street="Профсоюзная", house_number="25",
                latitude=55.671, longitude=37.560
            ),
            Location.objects.create(
                city="СПБ", street="Невский", house_number="30",
                latitude=59.934, longitude=30.335
            ),
            Location.objects.create(
                city="СПБ", street="Московский", house_number="40",
                latitude=59.910, longitude=30.320
            ),
            Location.objects.create(
                city="Казань", street="Баумана", house_number="5",
                latitude=55.796, longitude=49.106
            ),
        ]

        # 2. создаем теги
        self.stdout.write("создаем теги...")
        tags = {}
        for tag_name in ["economy", "comfort", "business", "sport", "electric", "family", "luxury"]:
            tag, _ = CarTag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag

        # 3. создаем автомобили
        self.stdout.write("создаем автомобили...")
        cars_data = [
            ("Toyota", "Camry", 2022, "A001AA", 7.5, "comfort", 5, SteeringType.AUTOMATIC, "70L",
             "Комфортный седан для городских поездок", locations[0]),
            ("Kia", "Rio", 2023, "A002BB", 5.0, "economy", 4, SteeringType.AUTOMATIC, "50L",
             "Экономичный и надежный автомобиль", locations[1]),
            ("Hyundai", "Solaris", 2022, "A003CC", 5.0, "economy", 4, SteeringType.AUTOMATIC, "55L",
             "Популярный городской автомобиль", locations[1]),
            ("Mercedes", "E-Class", 2023, "A004DD", 15.0, "business", 5, SteeringType.AUTOMATIC, "80L",
             "Премиальный бизнес-седан", locations[2]),
            ("BMW", "X5", 2022, "A005EE", 18.0, "luxury", 5, SteeringType.AUTOMATIC, "90L",
             "Мощный внедорожник премиум класса", locations[2]),
            ("Tesla", "Model 3", 2023, "A006FF", 12.0, "electric", 5, SteeringType.ELECTRIC, "0L",
             "Электрический седан с автопилотом", locations[3]),
            ("Volkswagen", "Polo", 2022, "A007GG", 4.5, "economy", 4, SteeringType.MANUAL, "45L",
             "Компактный хэтчбек для города", locations[4]),
            ("Skoda", "Octavia", 2023, "A008HH", 6.0, "comfort", 5, SteeringType.AUTOMATIC, "60L",
             "Просторный лифтбек для семьи", locations[0]),
            ("Renault", "Logan", 2022, "A009II", 4.0, "economy", 4, SteeringType.MANUAL, "50L", "Бюджетный седан",
             locations[5]),
            ("Lada", "Vesta", 2023, "A010JJ", 3.5, "economy", 4, SteeringType.MANUAL, "55L", "Отечественный автомобиль",
             locations[5]),
            ("Ford", "Focus", 2022, "A011KK", 6.5, "comfort", 5, SteeringType.AUTOMATIC, "60L", "Динамичный хэтчбек",
             locations[6]),
            ("Nissan", "Qashqai", 2023, "A012LL", 8.0, "family", 5, SteeringType.AUTOMATIC, "65L",
             "Компактный кроссовер для семьи", locations[6]),
            ("Honda", "Civic", 2022, "A013MM", 7.0, "sport", 4, SteeringType.AUTOMATIC, "50L", "Спортивный седан",
             locations[7]),
            ("Audi", "A4", 2023, "A014NN", 14.0, "business", 5, SteeringType.AUTOMATIC, "70L", "Немецкий бизнес-класс",
             locations[3]),
            ("Lexus", "RX", 2022, "A015OO", 20.0, "luxury", 5, SteeringType.AUTOMATIC, "85L", "Японская роскошь",
             locations[2]),
            ("Volvo", "XC60", 2023, "A016PP", 16.0, "family", 5, SteeringType.AUTOMATIC, "75L",
             "Безопасный семейный кроссовер", locations[0]),
            ("Porsche", "Cayenne", 2023, "A017QQ", 25.0, "luxury", 5, SteeringType.AUTOMATIC, "100L",
             "Спортивный внедорожник", locations[2]),
            ("Chevrolet", "Cruze", 2022, "A018RR", 6.0, "comfort", 5, SteeringType.AUTOMATIC, "60L",
             "Американский седан", locations[4]),
            ("Mazda", "CX-5", 2023, "A019SS", 9.0, "family", 5, SteeringType.AUTOMATIC, "65L", "Японский кроссовер",
             locations[1]),
            ("Subaru", "Outback", 2022, "A020TT", 11.0, "family", 5, SteeringType.AUTOMATIC, "70L",
             "Полноприводный универсал", locations[7]),
            ("Kia", "Sportage", 2023, "A021UU", 9.5, "family", 5, SteeringType.AUTOMATIC, "65L",
             "Стильный корейский кроссовер", locations[6]),
            ("Hyundai", "Tucson", 2022, "A022VV", 9.0, "family", 5, SteeringType.AUTOMATIC, "65L",
             "Современный городской кроссовер", locations[5]),
            ("Tesla", "Model X", 2023, "A023WW", 22.0, "electric", 7, SteeringType.ELECTRIC, "0L",
             "Электрический минивэн с крыльями", locations[3]),
        ]

        created_cars = []
        for brand, model, year, plate, price, tag_name, capacity, steering, gasoline, description, location in cars_data:
            car = Car.objects.create(
                brand=brand,
                model=model,
                year=year,
                plate_number=plate,
                price_per_minute=Decimal(price),
                location=location,
                status=CarStatus.AVAILABLE,
                capacity=capacity,
                steering=steering,
                gasoline=gasoline,
                description=description
            )
            car.tags.add(tags[tag_name])

            # добавляем дополнительный тег
            if "electric" in model.lower() or "Tesla" in brand:
                car.tags.add(tags["electric"])
            if price > 15:
                car.tags.add(tags["luxury"])

            # добавляем 2-3 случайных изображения
            for i in range(3):
                CarImage.objects.create(
                    car=car,
                    image="https://loremflickr.com/640/480/car",
                    is_main=(i == 0),
                    order=i
                )

            created_cars.append(car)

        # 4. создаем подписки
        self.stdout.write("создаем подписки...")
        subscriptions = {
            "Free": Subscription.objects.get_or_create(name="Free", defaults={"price": 0, "discount_percent": 0,
                                                                              "description": "базовый тариф"})[0],
            "Basic": Subscription.objects.get_or_create(name="Basic", defaults={"price": 499, "discount_percent": 10,
                                                                                "description": "скидка 10%"})[0],
            "Pro": Subscription.objects.get_or_create(name="Pro", defaults={"price": 999, "discount_percent": 20,
                                                                            "description": "скидка 20%"})[0],
        }

        # 5. создаем тестового пользователя
        self.stdout.write("создаем тестового пользователя...")
        test_user, created = User.objects.get_or_create(
            email="test@example.com",
            defaults={
                "phone": "+79991234567",
                "first_name": "Test",
                "last_name": "User",
                "verification_status": VerificationStatus.VERIFIED,
                "role": Role.USER,
                "is_active": True,
            }
        )
        if created:
            test_user.set_password("test123456")
            test_user.save()
            UserSubscription.objects.create(
                user=test_user,
                subscription=subscriptions["Basic"],
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30)
            )

        # 6. создаем администратора
        self.stdout.write("создаем администратора...")
        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "phone": "+79876543210",
                "first_name": "Admin",
                "last_name": "System",
                "verification_status": VerificationStatus.VERIFIED,
                "role": Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            }
        )
        if created:
            admin_user.set_password("admin123456")
            admin_user.save()

        # выводим статистику
        self.stdout.write(self.style.SUCCESS(f"""
        ========================================
        база данных успешно наполнена
        ========================================
        локаций: {len(locations)}
        тегов: {len(tags)}
        автомобилей: {len(created_cars)}
        изображений: {CarImage.objects.count()}
        подписок: {len(subscriptions)}
        пользователей: {User.objects.count()}
        ========================================
        тестовые учетные данные:
        пользователь: test@example.com / test123456
        администратор: admin@example.com / admin123456
        ========================================
        """))
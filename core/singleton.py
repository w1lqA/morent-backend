class SingletonMeta(type):
    """Метакласс для паттерна Singleton"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseConnection(metaclass=SingletonMeta):
    """Singleton для подключения к БД"""

    def __init__(self):
        self._connection = None
        self._connected = False

    def connect(self):
        if not self._connected:
            # Здесь будет реальное подключение
            print("🔌 Установлено соединение с базой данных")
            self._connected = True
        return self

    def disconnect(self):
        if self._connected:
            print("🔌 Соединение с БД закрыто")
            self._connected = False

    def execute_query(self, query):
        if not self._connected:
            raise Exception("Нет активного соединения с БД")
        print(f"📊 Выполняется запрос: {query}")
        # Здесь реальное выполнение запроса
        return True


class AuthService(metaclass=SingletonMeta):
    """Singleton для сервиса авторизации"""

    def __init__(self):
        self._current_user = None

    def login(self, email, password):
        # Проверка логина
        print(f"🔐 Авторизация пользователя: {email}")
        self._current_user = email
        return True

    def logout(self):
        print(f"👋 Выход пользователя: {self._current_user}")
        self._current_user = None

    def get_current_user(self):
        return self._current_user


class PricingService(metaclass=SingletonMeta):
    """Singleton для сервиса расчета цен"""

    def __init__(self):
        self._strategies = {}

    def register_strategy(self, name, strategy):
        self._strategies[name] = strategy

    def calculate_price(self, minutes, strategy_name='default', base_price_per_minute=0):
        if strategy_name not in self._strategies:
            raise ValueError(f"стратегия {strategy_name} не зарегистрирована")
        return self._strategies[strategy_name].calculate(minutes, base_price_per_minute)
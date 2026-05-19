class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self):
        self._connection = None
        self._connected = False

    def connect(self):
        if not self._connected:
            print("установлено соединение с базой данных")
            self._connected = True
        return self

    def disconnect(self):
        if self._connected:
            print("соединение с бд закрыто")
            self._connected = False

    def execute_query(self, query):
        if not self._connected:
            raise Exception("нет активного соединения с бд")
        print(f"выполняется запрос: {query}")
        return True


class AuthService(metaclass=SingletonMeta):
    def __init__(self):
        self._current_user = None

    def login(self, email, password):
        print(f"авторизация пользователя: {email}")
        self._current_user = email
        return True

    def logout(self):
        print(f"выход пользователя: {self._current_user}")
        self._current_user = None

    def get_current_user(self):
        return self._current_user


class PricingService(metaclass=SingletonMeta):
    def __init__(self):
        self._strategies = {}

    def register_strategy(self, name, strategy):
        self._strategies[name] = strategy

    def calculate_price(self, minutes, strategy_name='default', base_price_per_minute=0):
        if strategy_name not in self._strategies:
            raise ValueError(f"стратегия {strategy_name} не зарегистрирована")
        return self._strategies[strategy_name].calculate(minutes, base_price_per_minute)
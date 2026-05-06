from abc import ABC, abstractmethod


# ========== COMPOSITE ==========

class CarComponent(ABC):
    """Компонент для иерархии автомобилей"""

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_count(self):
        pass

    @abstractmethod
    def display(self, indent=0):
        pass


class CarLeaf(CarComponent):
    """Отдельный автомобиль (лист)"""

    def __init__(self, car):
        self.car = car

    def get_price(self):
        return float(self.car.price_per_minute)

    def get_count(self):
        return 1

    def display(self, indent=0):
        print(" " * indent + f"🚗 {self.car.brand} {self.car.model} - {self.car.price_per_minute} руб/мин")


class CarCategory(CarComponent):
    """Категория автомобилей (композит)"""

    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, component):
        self._children.append(component)

    def remove(self, component):
        self._children.remove(component)

    def get_price(self):
        # Средняя цена по категории
        if not self._children:
            return 0
        total = sum(child.get_price() for child in self._children)
        return total / len(self._children)

    def get_count(self):
        return sum(child.get_count() for child in self._children)

    def display(self, indent=0):
        print(
            " " * indent + f"📁 {self.name} (всего: {self.get_count()} авто, средняя цена: {self.get_price():.2f} руб/мин)")
        for child in self._children:
            child.display(indent + 2)


class CarFleet(CarComponent):
    """Весь автопарк (корневой композит)"""

    def __init__(self, name="Автопарк"):
        self.name = name
        self._categories = []

    def add_category(self, category):
        self._categories.append(category)

    def get_price(self):
        if not self._categories:
            return 0
        total = sum(cat.get_price() for cat in self._categories)
        return total / len(self._categories)

    def get_count(self):
        return sum(cat.get_count() for cat in self._categories)

    def display(self, indent=0):
        print("=" * 50)
        print(f"🏢 {self.name}")
        print(f"📊 Всего автомобилей: {self.get_count()}")
        print(f"💰 Средняя цена по парку: {self.get_price():.2f} руб/мин")
        print("=" * 50)
        for category in self._categories:
            category.display(indent)


# ========== ITERATOR ==========

class CarIterator:
    """Итератор для перебора автомобилей"""

    def __init__(self, cars):
        self._cars = cars
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._cars):
            car = self._cars[self._index]
            self._index += 1
            return car
        raise StopIteration

    def first(self):
        if self._cars:
            self._index = 0
            return self._cars[0]
        return None

    def last(self):
        if self._cars:
            self._index = len(self._cars) - 1
            return self._cars[-1]
        return None


class CarFilterIterator(CarIterator):
    """Итератор с фильтрацией"""

    def __init__(self, cars, filter_func):
        filtered_cars = [car for car in cars if filter_func(car)]
        super().__init__(filtered_cars)
        self.filter_func = filter_func


class CarPaginationIterator:
    """Итератор для пагинации"""

    def __init__(self, cars, page_size=10):
        self._cars = cars
        self._page_size = page_size
        self._current_page = 0

    def get_page(self, page_number):
        start = page_number * self._page_size
        end = start + self._page_size
        return self._cars[start:end]

    def __iter__(self):
        for i in range(0, len(self._cars), self._page_size):
            yield self._cars[i:i + self._page_size]


class CategoryIterator:
    """Итератор для обхода дерева категорий"""

    def __init__(self, root_category):
        self._stack = [root_category]

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stack:
            raise StopIteration

        current = self._stack.pop()

        # Добавляем детей в стек (для глубины)
        if hasattr(current, '_children'):
            self._stack.extend(reversed(current._children))

        return current
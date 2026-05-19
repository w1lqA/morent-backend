from abc import ABC, abstractmethod


class CarComponent(ABC):
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
    def __init__(self, car):
        self.car = car

    def get_price(self):
        return float(self.car.price_per_minute)

    def get_count(self):
        return 1

    def display(self, indent=0):
        print(" " * indent + f"{self.car.brand} {self.car.model} - {self.car.price_per_minute} руб/мин")


class CarCategory(CarComponent):
    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, component):
        self._children.append(component)

    def remove(self, component):
        self._children.remove(component)

    def get_price(self):
        if not self._children:
            return 0
        total = sum(child.get_price() for child in self._children)
        return total / len(self._children)

    def get_count(self):
        return sum(child.get_count() for child in self._children)

    def display(self, indent=0):
        print(" " * indent + f"{self.name} (всего: {self.get_count()} авто, средняя цена: {self.get_price():.2f} руб/мин)")
        for child in self._children:
            child.display(indent + 2)


class CarFleet(CarComponent):
    def __init__(self, name="автопарк"):
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
        print(f"{self.name}")
        print(f"всего автомобилей: {self.get_count()}")
        print(f"средняя цена по парку: {self.get_price():.2f} руб/мин")
        print("=" * 50)
        for category in self._categories:
            category.display(indent)


class CarCollection:
    def __init__(self, cars=None):
        self._cars = cars or []
        self._index_map = {}

    def add(self, car):
        self._cars.append(car)
        self._reindex()

    def remove(self, car_id):
        self._cars = [c for c in self._cars if c.id != car_id]
        self._reindex()

    def get(self, index):
        if 0 <= index < len(self._cars):
            return self._cars[index]
        return None

    def size(self):
        return len(self._cars)

    def _reindex(self):
        self._index_map = {i: car for i, car in enumerate(self._cars)}

    def get_all(self):
        return self._cars.copy()

    def filter(self, predicate):
        return CarCollection([car for car in self._cars if predicate(car)])


class CarIterator:
    def __init__(self, collection):
        self._collection = collection
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < self._collection.size():
            car = self._collection.get(self._index)
            self._index += 1
            return car
        raise StopIteration

    def first(self):
        if self._collection.size() > 0:
            self._index = 0
            return self._collection.get(0)
        return None

    def last(self):
        size = self._collection.size()
        if size > 0:
            self._index = size - 1
            return self._collection.get(size - 1)
        return None

    def reset(self):
        self._index = 0


class CarFilterIterator(CarIterator):
    def __init__(self, collection, filter_func):
        filtered_collection = CarCollection([car for car in collection.get_all() if filter_func(car)])
        super().__init__(filtered_collection)
        self.filter_func = filter_func


class CarPaginationIterator:
    def __init__(self, collection, page_size=10):
        self._collection = collection
        self._page_size = page_size
        self._current_page = 0

    def get_page(self, page_number):
        start = page_number * self._page_size
        end = start + self._page_size
        page_cars = []
        for i in range(start, min(end, self._collection.size())):
            car = self._collection.get(i)
            if car:
                page_cars.append(car)
        return page_cars

    def __iter__(self):
        for i in range(0, self._collection.size(), self._page_size):
            yield self.get_page(i // self._page_size)

    def total_pages(self):
        return (self._collection.size() + self._page_size - 1) // self._page_size


class CategoryIterator:
    def __init__(self, root_category):
        self._stack = [root_category]

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stack:
            raise StopIteration
        current = self._stack.pop()
        if hasattr(current, '_children'):
            self._stack.extend(reversed(current._children))
        return current
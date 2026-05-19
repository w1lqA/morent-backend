from abc import ABC, abstractmethod


class PriceStrategy(ABC):
    @abstractmethod
    def calculate(self, minutes, base_price_per_minute):
        pass


class DefaultPriceStrategy(PriceStrategy):
    def calculate(self, minutes, base_price_per_minute):
        return minutes * base_price_per_minute


class SubscriptionPriceStrategy(PriceStrategy):
    def __init__(self, discount_percent=10):
        self.discount_percent = discount_percent

    def calculate(self, minutes, base_price_per_minute):
        subtotal = minutes * base_price_per_minute
        discount = subtotal * self.discount_percent / 100
        return subtotal - discount


class PromotionPriceStrategy(PriceStrategy):
    def __init__(self, promotion_discount):
        self.promotion_discount = promotion_discount

    def calculate(self, minutes, base_price_per_minute):
        subtotal = minutes * base_price_per_minute
        discount = subtotal * self.promotion_discount / 100
        return subtotal - discount


class CombinedDiscountStrategy(PriceStrategy):
    def __init__(self, subscription_discount=10, promotion_discount=0):
        self.subscription_discount = subscription_discount
        self.promotion_discount = promotion_discount

    def calculate(self, minutes, base_price_per_minute):
        subtotal = minutes * base_price_per_minute
        after_subscription = subtotal * (100 - self.subscription_discount) / 100
        return after_subscription * (100 - self.promotion_discount) / 100


class LicenseCategoryStrategy(PriceStrategy):
    def __init__(self, license_category):
        self.license_category = license_category
        self.multipliers = {
            'A': 1.2,
            'B': 1.0,
            'C': 1.5
        }

    def calculate(self, minutes, base_price_per_minute):
        multiplier = self.multipliers.get(self.license_category, 1.0)
        return minutes * base_price_per_minute * multiplier
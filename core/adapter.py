from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    """Целевой интерфейс для платежной системы"""

    @abstractmethod
    def process_payment(self, amount, currency):
        pass

    @abstractmethod
    def refund_payment(self, transaction_id):
        pass


class ExternalPaymentService:
    """Сторонний платежный сервис (адаптируемый)"""

    def make_transaction(self, amount_usd, card_info):
        print(f"💳 ExternalService: платеж на {amount_usd} USD")
        return {"txn_id": f"EXT_{hash(amount_usd)}", "status": "success"}

    def cancel_transaction(self, external_id):
        print(f"💳 ExternalService: возврат платежа {external_id}")
        return True


class PaymentAdapter(PaymentGateway):
    """Адаптер для интеграции внешнего платежного сервиса"""

    def __init__(self, external_service):
        self._external = external_service

    def process_payment(self, amount, currency):
        # Конвертация в USD (для примера)
        if currency == "RUB":
            amount_usd = amount / 100  # условно 100 RUB = 1 USD
        else:
            amount_usd = amount

        result = self._external.make_transaction(amount_usd, "saved_card")
        return {
            "success": True,
            "transaction_id": result["txn_id"]
        }

    def refund_payment(self, transaction_id):
        return self._external.cancel_transaction(transaction_id)


class NotificationService:
    """Адаптер для уведомлений"""

    def send_sms(self, phone, message):
        print(f"📱 SMS на {phone}: {message}")
        return True

    def send_email(self, email, subject, body):
        print(f"📧 Email на {email}: {subject}")
        return True

class PaymentError(Exception):
    def __init__(self, message):
        self.message = str(message)


class BasketValidationError(Exception):
    def __init__(self, message, reason_code):
        self.message = str(message)
        self.reason_code = reason_code

class PaymentNotFoundError(Exception):
    def __init__(self, payment_id: str) -> None:
        self.payment_id = payment_id
        super().__init__(f"Payment not found: {payment_id}")

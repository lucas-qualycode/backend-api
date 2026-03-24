from domain.payments.entity import Payment
from domain.payments.exceptions import PaymentNotFoundError
from domain.payments.repository import PaymentRepository


def get_payment(repo: PaymentRepository, payment_id: str) -> Payment:
    payment = repo.get_by_id(payment_id)
    if payment is None:
        raise PaymentNotFoundError(payment_id)
    return payment

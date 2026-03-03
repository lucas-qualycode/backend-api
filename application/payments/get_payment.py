from backend_api.domain.payments.entity import Payment
from backend_api.domain.payments.exceptions import PaymentNotFoundError
from backend_api.domain.payments.repository import PaymentRepository


def get_payment(repo: PaymentRepository, payment_id: str) -> Payment:
    payment = repo.get_by_id(payment_id)
    if payment is None:
        raise PaymentNotFoundError(payment_id)
    return payment

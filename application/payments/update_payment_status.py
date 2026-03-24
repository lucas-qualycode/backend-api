from domain.payments.entity import Payment
from domain.payments.exceptions import PaymentNotFoundError
from domain.payments.repository import PaymentRepository


def update_payment_status(
    repo: PaymentRepository,
    payment_id: str,
    status: str,
) -> Payment:
    result = repo.update_status(payment_id, status)
    if result is None:
        raise PaymentNotFoundError(payment_id)
    return result

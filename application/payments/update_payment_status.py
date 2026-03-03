from backend_api.domain.payments.entity import Payment
from backend_api.domain.payments.exceptions import PaymentNotFoundError
from backend_api.domain.payments.repository import PaymentRepository


def update_payment_status(
    repo: PaymentRepository,
    payment_id: str,
    status: str,
) -> Payment:
    result = repo.update_status(payment_id, status)
    if result is None:
        raise PaymentNotFoundError(payment_id)
    return result

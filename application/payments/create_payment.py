import uuid

from backend_api.application.payments.schemas import CreatePaymentInput
from backend_api.domain.payments.entity import Payment
from backend_api.domain.payments.repository import PaymentRepository


def create_payment(
    repo: PaymentRepository,
    data: CreatePaymentInput,
    now: str,
) -> Payment:
    payment = Payment(
        id=str(uuid.uuid4()),
        order_id=data.order_id,
        user_id=data.user_id,
        amount=data.amount,
        currency=data.currency,
        status=data.status,
        payment_provider=data.payment_provider,
        payment_provider_payment_id=data.payment_provider_payment_id,
        payment_method=data.payment_method,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
    )
    return repo.create(payment)

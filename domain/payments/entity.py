from typing import ClassVar

from pydantic import BaseModel


class Payment(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: int
    currency: str
    status: str
    payment_provider: str
    payment_provider_payment_id: str | None = None
    payment_method: str | None = None
    created_at: str
    updated_at: str
    metadata: dict = {}


class PaymentQueryParams(BaseModel):
    user_id: str | None = None
    order_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("user_id", "user_id", "=="),
        ("order_id", "order_id", "=="),
        ("status", "status", "=="),
    ]


class PaymentStatus:
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

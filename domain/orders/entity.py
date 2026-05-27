from typing import ClassVar
from pydantic import BaseModel

class OrderItem(BaseModel):
    id: str
    product_id: str
    product_type: str | None = None
    quantity: int
    unit_price: int
    total_price: int
    currency: str
    metadata: dict = {}

class Order(BaseModel):
    id: str
    user_id: str
    parent_id: str | None = None
    invitation_id: str | None = None
    items: list[OrderItem]
    subtotal: int
    tax_amount: int
    discount_amount: int
    total_amount: int
    currency: str
    status: str
    payment_provider: str = "mercadopago"
    created_at: str
    updated_at: str
    expires_at: str
    metadata: dict = {}

class OrderQueryParams(BaseModel):
    user_id: str | None = None
    parent_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None
    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("user_id", "user_id", "=="),
        ("parent_id", "parent_id", "=="),
        ("status", "status", "=="),
    ]

class OrderStatus:
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    EXPIRED = "EXPIRED"

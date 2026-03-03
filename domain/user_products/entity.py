from typing import ClassVar

from pydantic import BaseModel


class UserProduct(BaseModel):
    id: str
    parent_id: str
    product_id: str
    user_id: str
    invitation_id: str | None = None
    quantity: int
    status: str
    purchase_date: str
    valid_from: str
    valid_until: str | None = None
    price: int
    currency: str
    payment_id: str | None = None
    created_at: str
    updated_at: str
    metadata: dict = {}
    additional_data: dict = {}


class UserProductQueryParams(BaseModel):
    parent_id: str | None = None
    user_id: str | None = None
    product_id: str | None = None
    status: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("parent_id", "parent_id", "=="),
        ("user_id", "user_id", "=="),
        ("product_id", "product_id", "=="),
        ("status", "status", "=="),
    ]

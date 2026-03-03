from typing import ClassVar

from pydantic import BaseModel


class InventoryItem(BaseModel):
    id: str
    product_type: str
    product_id: str
    available_quantity: int
    reserved_quantity: int
    total_quantity: int
    price: int
    currency: str
    created_at: str
    updated_at: str
    metadata: dict = {}


class InventoryQueryParams(BaseModel):
    product_id: str | None = None
    product_type: str | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("product_id", "product_id", "=="),
        ("product_type", "product_type", "=="),
    ]

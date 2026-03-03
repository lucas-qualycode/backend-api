from typing import ClassVar

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    description: str
    parent_id: str | None = None
    parent_type: str | None = None
    type: str | None = None
    user_id: str
    is_free: bool
    value: int
    quantity: int
    max_per_user: int
    request_additional_info: bool
    active: bool = True
    deleted: bool = False
    created_at: str
    updated_at: str
    created_by: str
    last_updated_by: str
    metadata: dict = {}


class ProductQueryParams(BaseModel):
    name: str | None = None
    parent_id: str | None = None
    active: bool | None = None
    deleted: bool | None = None
    limit: int | None = None
    offset: int | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("parent_id", "parent_id", "=="),
        ("active", "active", "=="),
        ("deleted", "deleted", "=="),
    ]

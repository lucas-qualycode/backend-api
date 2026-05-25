from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator

from domain.products.types import FulfillmentType, ProductType


class ProductAdditionalInfoFieldRef(BaseModel):
    field_id: str
    label: str | None = None
    required: bool | None = None
    order: int | None = None
    active: bool | None = None


class Product(BaseModel):
    id: str
    name: str
    description: str
    imageURL: str | None = None
    parent_id: str | None = None
    parent_type: str | None = None
    type: ProductType = ProductType.MERCH
    user_id: str
    is_free: bool
    value: int
    quantity: int
    max_per_user: int
    additional_info_fields: list[ProductAdditionalInfoFieldRef] = Field(default_factory=list)
    fulfillment_type: FulfillmentType | None = None
    fulfillment_profile_id: str | None = None
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
    type: ProductType | None = None
    active: bool | None = None
    deleted: bool | None = None
    limit: int | None = None
    offset: int | None = None
    tag_id: str | None = None

    FILTER_SPEC: ClassVar[list[tuple[str, str, str]]] = [
        ("parent_id", "parent_id", "=="),
        ("type", "type", "=="),
        ("active", "active", "=="),
        ("deleted", "deleted", "=="),
    ]



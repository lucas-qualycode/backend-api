from pydantic import BaseModel, Field

from domain.products.types import FulfillmentType, ProductType


class ProductAdditionalInfoFieldRefInput(BaseModel):
    field_id: str
    label: str | None = None
    required: bool | None = None
    order: int | None = None
    active: bool | None = None


class CreateProductInput(BaseModel):
    name: str
    description: str
    imageURL: str | None = None
    parent_id: str | None = None
    parent_type: str | None = None
    type: ProductType = ProductType.MERCH
    fulfillment_type: FulfillmentType | None = None
    fulfillment_profile_id: str | None = None
    is_free: bool
    value: int
    quantity: int
    max_per_user: int
    additional_info_fields: list[ProductAdditionalInfoFieldRefInput] = Field(default_factory=list)
    active: bool = True
    metadata: dict = {}
    tag_ids: list[str] = []


class UpdateProductInput(BaseModel):
    name: str | None = None
    description: str | None = None
    imageURL: str | None = None
    parent_id: str | None = None
    parent_type: str | None = None
    type: ProductType | None = None
    fulfillment_type: FulfillmentType | None = None
    fulfillment_profile_id: str | None = None
    is_free: bool | None = None
    value: int | None = None
    quantity: int | None = None
    max_per_user: int | None = None
    additional_info_fields: list[ProductAdditionalInfoFieldRefInput] | None = None
    active: bool | None = None
    metadata: dict | None = None
    tag_ids: list[str] | None = None

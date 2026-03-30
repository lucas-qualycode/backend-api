from pydantic import BaseModel


class CreateProductInput(BaseModel):
    name: str
    description: str
    imageURL: str | None = None
    parent_id: str | None = None
    parent_type: str | None = None
    type: str | None = None
    is_free: bool
    value: int
    quantity: int
    max_per_user: int
    request_additional_info: bool
    active: bool = True
    metadata: dict = {}
    tag_ids: list[str] = []


class UpdateProductInput(BaseModel):
    name: str | None = None
    description: str | None = None
    imageURL: str | None = None
    parent_id: str | None = None
    parent_type: str | None = None
    type: str | None = None
    is_free: bool | None = None
    value: int | None = None
    quantity: int | None = None
    max_per_user: int | None = None
    request_additional_info: bool | None = None
    active: bool | None = None
    metadata: dict | None = None
    tag_ids: list[str] | None = None

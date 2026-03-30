from pydantic import BaseModel


class CreateUserProductRequest(BaseModel):
    parent_id: str
    product_id: str
    invitation_id: str | None = None
    quantity: int
    status: str
    purchase_date: str
    valid_from: str
    valid_until: str | None = None
    price: int
    currency: str
    payment_id: str | None = None
    metadata: dict = {}
    additional_data: dict = {}


class CreateUserProductInput(BaseModel):
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
    metadata: dict = {}
    additional_data: dict = {}


class UpdateUserProductInput(BaseModel):
    parent_id: str | None = None
    product_id: str | None = None
    user_id: str | None = None
    invitation_id: str | None = None
    quantity: int | None = None
    status: str | None = None
    purchase_date: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    price: int | None = None
    currency: str | None = None
    payment_id: str | None = None
    metadata: dict | None = None
    additional_data: dict | None = None

from pydantic import BaseModel


class OrderItemInput(BaseModel):
    product_id: str
    product_type: str | None = None
    quantity: int
    unit_price: int
    total_price: int | None = None
    currency: str
    metadata: dict = {}


class CreateOrderRequest(BaseModel):
    parent_id: str | None = None
    invitation_id: str | None = None
    items: list[OrderItemInput]
    currency: str
    metadata: dict = {}
    expires_at: str | None = None


class CreateOrderInput(BaseModel):
    user_id: str
    parent_id: str | None = None
    invitation_id: str | None = None
    items: list[OrderItemInput]
    currency: str
    metadata: dict = {}
    expires_at: str | None = None


class UpdateOrderStatusInput(BaseModel):
    status: str

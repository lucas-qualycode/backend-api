from typing import Any, Literal

from pydantic import BaseModel, Field

from domain.products.types import ProductType

PaymentProviderId = Literal["mercadopago"]


class OrderItemInput(BaseModel):
    product_id: str
    product_type: ProductType | None = None
    quantity: int = 1
    unit_price: int
    total_price: int | None = None
    currency: str = "BRL"
    metadata: dict[str, Any] = Field(default_factory=dict)
    name: str | None = None


class CreateOrderRequest(BaseModel):
    parent_id: str | None = None
    invitation_id: str | None = None
    items: list[OrderItemInput]
    currency: str = "BRL"
    metadata: dict[str, Any] = Field(default_factory=dict)
    expires_at: str | None = None
    total_cents: int | None = None
    payment_provider: PaymentProviderId | None = None


class CreateOrderInput(BaseModel):
    user_id: str
    parent_id: str | None = None
    invitation_id: str | None = None
    items: list[OrderItemInput]
    currency: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    expires_at: str | None = None
    payment_provider: PaymentProviderId | None = None


class UpdateOrderStatusInput(BaseModel):
    status: str


class InvitationCheckoutRequest(CreateOrderRequest):
    payment_provider: PaymentProviderId
    provider_checkout: dict[str, Any]

    model_config = {"extra": "ignore"}


class InvitationCheckoutResponse(BaseModel):
    order_id: str
    payment_id: str
    payment_provider_payment_id: str | None = None
    idempotent_replay: bool = False

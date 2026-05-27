from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from domain.products.types import ProductType

PaymentProviderId = Literal["mercadopago"]


class OrderItemInput(BaseModel):
    product_id: str
    product_type: ProductType | None = None
    quantity: int = 1
    unit_price: int | None = None
    total_price: int | None = None
    currency: str = "BRL"
    metadata: dict[str, Any] = Field(default_factory=dict)
    name: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_price_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        row = dict(data)
        if row.get("unit_price") is None and row.get("unit_price_cents") is not None:
            row["unit_price"] = row.pop("unit_price_cents")
        if row.get("total_price") is None and row.get("total_price_cents") is not None:
            row["total_price"] = row.pop("total_price_cents")
        return row

    @model_validator(mode="after")
    def require_unit_price(self) -> "OrderItemInput":
        if self.unit_price is None:
            raise ValueError("unit_price or unit_price_cents is required")
        return self


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

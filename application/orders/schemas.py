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


class PixDisplayPayload(BaseModel):
    qr_code_base64: str | None = None
    copy_paste_code: str | None = None
    ticket_url: str | None = None
    expires_at: str | None = None


class PaymentFailurePayload(BaseModel):
    code: str | None = None
    message: str | None = None


PaymentNextAction = Literal["display_pix", "wait", "done", "failed"]


class PaymentOutcomeFields(BaseModel):
    payment_status: str = "PENDING"
    payment_method: str | None = None
    next_action: PaymentNextAction = "wait"
    total_cents: int | None = None
    pix: PixDisplayPayload | None = None
    failure: PaymentFailurePayload | None = None


class InvitationCheckoutResponse(PaymentOutcomeFields):
    order_id: str
    payment_id: str
    payment_provider_payment_id: str | None = None
    idempotent_replay: bool = False


class ActiveCheckoutResponse(PaymentOutcomeFields):
    payment_status: str | None = None
    next_action: PaymentNextAction | None = None
    active: bool = False
    order_id: str | None = None
    payment_id: str | None = None
    has_approved_payment: bool = False


class GuestPaymentStatusResponse(PaymentOutcomeFields):
    order_id: str
    payment_id: str
    payment_provider_payment_id: str | None = None


class ConfirmationOrderItemSummary(BaseModel):
    product_id: str
    name: str | None = None
    quantity: int
    unit_price: int
    total_price: int


class ConfirmationOrderSummary(BaseModel):
    id: str
    total_amount: int
    currency: str
    items: list[ConfirmationOrderItemSummary] = Field(default_factory=list)


class ConfirmationPaymentSummary(BaseModel):
    id: str
    status: str
    payment_method: str | None = None
    amount: int
    currency: str
    created_at: str
    payment_provider_payment_id: str | None = None
    order: ConfirmationOrderSummary | None = None


class InvitationConfirmationResponse(BaseModel):
    invitation_id: str
    event_id: str
    guest_slots: list[dict[str, Any]] = Field(default_factory=list)
    couple_message: str | None = None
    payments: list[ConfirmationPaymentSummary] = Field(default_factory=list)

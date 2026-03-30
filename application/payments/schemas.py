from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: int
    currency: str
    status: str
    payment_provider: str
    payment_provider_payment_id: str | None = None
    payment_method: str | None = None
    metadata: dict = {}


class CreatePaymentInput(BaseModel):
    order_id: str
    user_id: str
    amount: int
    currency: str
    status: str
    payment_provider: str
    payment_provider_payment_id: str | None = None
    payment_method: str | None = None
    metadata: dict = {}


class UpdatePaymentStatusInput(BaseModel):
    status: str

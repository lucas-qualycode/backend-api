from typing import Any

from application.orders.schemas import (
    GuestPaymentStatusResponse,
    InvitationCheckoutResponse,
    PaymentFailurePayload,
)
from domain.payments.entity import Payment, PaymentStatus
from infrastructure.mercadopago.order_response import (
    MappedProviderPayment,
    map_provider_order_response,
)


def mapped_to_checkout_fields(mapped: MappedProviderPayment, *, total_cents: int | None = None) -> dict[str, Any]:
    return {
        "payment_status": mapped.payment_status,
        "payment_method": mapped.payment_method,
        "next_action": mapped.next_action,
        "total_cents": total_cents,
        "pix": mapped.pix.model_dump(mode="json") if mapped.pix else None,
        "failure": mapped.failure.model_dump(mode="json") if mapped.failure else None,
    }


def build_checkout_response(
    *,
    order_id: str,
    payment_id: str,
    payment_provider_payment_id: str | None,
    mapped: MappedProviderPayment,
    total_cents: int,
    idempotent_replay: bool = False,
) -> InvitationCheckoutResponse:
    return InvitationCheckoutResponse(
        order_id=order_id,
        payment_id=payment_id,
        payment_provider_payment_id=payment_provider_payment_id,
        idempotent_replay=idempotent_replay,
        **mapped_to_checkout_fields(mapped, total_cents=total_cents),
    )


def build_guest_payment_status_response(
    *,
    order_id: str,
    payment: Payment,
    mapped: MappedProviderPayment,
) -> GuestPaymentStatusResponse:
    return GuestPaymentStatusResponse(
        order_id=order_id,
        payment_id=payment.id,
        payment_provider_payment_id=payment.payment_provider_payment_id,
        **mapped_to_checkout_fields(mapped, total_cents=payment.amount),
    )


def apply_mapped_status_to_payment(payment: Payment, mapped: MappedProviderPayment, now: str) -> Payment:
    metadata = dict(payment.metadata or {})
    if mapped.failure and mapped.payment_status in (PaymentStatus.FAILED, PaymentStatus.CANCELLED):
        metadata["provider_failure"] = mapped.failure.model_dump(mode="json")
    return payment.model_copy(
        update={
            "status": mapped.payment_status,
            "metadata": metadata,
            "updated_at": now,
        }
    )


def map_stored_provider_response(provider_response: dict[str, Any] | None) -> MappedProviderPayment:
    if not provider_response:
        return MappedProviderPayment(
            payment_status=PaymentStatus.PENDING,
            payment_method=None,
            next_action="wait",
        )
    return map_provider_order_response(provider_response)

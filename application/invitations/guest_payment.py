from typing import Any

from application.invitations.checkout import guest_user_id
from application.invitations.payment_outcome import build_guest_payment_status_response
from application.orders.schemas import ActiveCheckoutResponse, GuestPaymentStatusResponse
from domain.orders.entity import OrderQueryParams
from domain.orders.repository import OrderRepository
from domain.payments.entity import Payment, PaymentQueryParams, PaymentStatus
from domain.payments.exceptions import PaymentNotFoundError
from domain.payments.repository import PaymentRepository
from infrastructure.mercadopago.order_response import (
    MappedProviderPayment,
    build_payment_outcome_from_stored,
)
from utils.errors import ValidationError

_TERMINAL_STATUSES = frozenset({PaymentStatus.FAILED, PaymentStatus.CANCELLED})


def _provider_response(payment: Payment) -> dict[str, Any] | None:
    raw = (payment.metadata or {}).get("provider_response")
    return raw if isinstance(raw, dict) else None


def _payment_belongs_to_invitation(payment: Payment, order_invitation_id: str | None, invitation_id: str) -> bool:
    if order_invitation_id == invitation_id:
        return True
    return payment.user_id == guest_user_id(invitation_id)


def _payments_for_order(payment_repo: PaymentRepository, order_id: str) -> list[Payment]:
    return payment_repo.list(PaymentQueryParams(order_id=order_id, limit=50))


def _mapped_outcome_from_payment(payment: Payment) -> MappedProviderPayment:
    provider_response = _provider_response(payment)
    return build_payment_outcome_from_stored(
        payment_status=payment.status,
        payment_method=payment.payment_method,
        provider_response=provider_response,
    )


def _resolve_next_action(payment: Payment, mapped: MappedProviderPayment) -> str:
    if payment.status == PaymentStatus.APPROVED:
        return "done"
    if payment.status in _TERMINAL_STATUSES:
        return "failed"
    if payment.status == PaymentStatus.PENDING:
        return mapped.next_action
    return mapped.next_action


def _checkout_fields_from_payment(
    order_id: str,
    payment: Payment,
    *,
    active: bool,
    has_approved_payment: bool,
) -> dict[str, Any]:
    mapped = _mapped_outcome_from_payment(payment)
    method = payment.payment_method or mapped.payment_method
    return {
        "active": active,
        "order_id": order_id,
        "payment_id": payment.id,
        "has_approved_payment": has_approved_payment,
        "payment_status": payment.status,
        "payment_method": method,
        "next_action": _resolve_next_action(payment, mapped),
        "total_cents": payment.amount,
        "pix": mapped.pix.model_dump(mode="json") if mapped.pix else None,
        "failure": mapped.failure.model_dump(mode="json") if mapped.failure else None,
    }


def get_active_checkout(
    invitation_id: str,
    *,
    order_repo: OrderRepository,
    payment_repo: PaymentRepository,
) -> ActiveCheckoutResponse:
    orders = order_repo.list(
        OrderQueryParams(invitation_id=invitation_id, limit=20),
    )
    orders_sorted = sorted(orders, key=lambda o: o.created_at, reverse=True)

    has_approved_payment = False
    latest_approved: ActiveCheckoutResponse | None = None
    latest_terminal: ActiveCheckoutResponse | None = None
    for order in orders_sorted:
        payments = _payments_for_order(payment_repo, order.id)
        if not payments:
            continue
        payment = sorted(payments, key=lambda p: p.created_at, reverse=True)[0]

        if payment.status == PaymentStatus.APPROVED:
            has_approved_payment = True
            if latest_approved is None:
                latest_approved = ActiveCheckoutResponse(
                    **_checkout_fields_from_payment(
                        order.id,
                        payment,
                        active=False,
                        has_approved_payment=True,
                    ),
                )
            continue

        if payment.status in (PaymentStatus.PENDING, PaymentStatus.PROCESSING):
            fields = _checkout_fields_from_payment(
                order.id,
                payment,
                active=True,
                has_approved_payment=has_approved_payment,
            )
            return ActiveCheckoutResponse(**fields)

        if payment.status in _TERMINAL_STATUSES and latest_terminal is None:
            latest_terminal = ActiveCheckoutResponse(
                **_checkout_fields_from_payment(
                    order.id,
                    payment,
                    active=False,
                    has_approved_payment=has_approved_payment,
                ),
            )

    if latest_approved:
        return latest_approved

    if latest_terminal:
        return latest_terminal

    return ActiveCheckoutResponse(active=False, has_approved_payment=has_approved_payment)


def get_guest_payment_status(
    invitation_id: str,
    payment_id: str,
    *,
    order_repo: OrderRepository,
    payment_repo: PaymentRepository,
) -> GuestPaymentStatusResponse:
    payment = payment_repo.get_by_id(payment_id)
    if payment is None:
        raise PaymentNotFoundError(payment_id)

    order = order_repo.get_by_id(payment.order_id)
    if order is None:
        raise ValidationError("Order not found for payment")

    if not _payment_belongs_to_invitation(payment, order.invitation_id, invitation_id):
        raise ValidationError("Payment does not belong to this invitation")

    mapped = _mapped_outcome_from_payment(payment)
    if payment.status == PaymentStatus.APPROVED:
        mapped = mapped.model_copy(update={"next_action": "done"})
    elif payment.status in _TERMINAL_STATUSES:
        mapped = mapped.model_copy(update={"next_action": "failed"})

    return build_guest_payment_status_response(
        order_id=order.id,
        payment=payment,
        mapped=mapped,
    )

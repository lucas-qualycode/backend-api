from application.invitations.checkout import guest_user_id
from application.orders.schemas import (
    ConfirmationOrderItemSummary,
    ConfirmationOrderSummary,
    ConfirmationPaymentSummary,
    InvitationConfirmationResponse,
)
from domain.invitations.entity import Invitation
from domain.invitation_guest_slots.repository import InvitationGuestSlotRepository
from domain.orders.entity import OrderQueryParams
from domain.orders.repository import OrderRepository
from domain.payments.entity import PaymentQueryParams, PaymentStatus
from domain.payments.repository import PaymentRepository


def get_invitation_confirmation(
    invitation: Invitation,
    *,
    order_repo: OrderRepository,
    payment_repo: PaymentRepository,
    guest_slot_repo: InvitationGuestSlotRepository,
) -> InvitationConfirmationResponse:
    invitation_id = invitation.id
    orders = order_repo.list(
        OrderQueryParams(invitation_id=invitation_id, limit=50),
    )
    orders_sorted = sorted(orders, key=lambda o: o.created_at, reverse=True)

    payment_summaries: list[ConfirmationPaymentSummary] = []
    for order in orders_sorted:
        payments = payment_repo.list(PaymentQueryParams(order_id=order.id, limit=20))
        for payment in sorted(payments, key=lambda p: p.created_at, reverse=True):
            if payment.user_id != guest_user_id(invitation_id) and order.invitation_id != invitation_id:
                continue
            items = [
                ConfirmationOrderItemSummary(
                    product_id=item.product_id,
                    name=(item.metadata or {}).get("display_name"),
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                for item in order.items
            ]
            payment_summaries.append(
                ConfirmationPaymentSummary(
                    id=payment.id,
                    status=payment.status,
                    payment_method=payment.payment_method,
                    amount=payment.amount,
                    currency=payment.currency,
                    created_at=payment.created_at,
                    payment_provider_payment_id=payment.payment_provider_payment_id,
                    order=ConfirmationOrderSummary(
                        id=order.id,
                        total_amount=order.total_amount,
                        currency=order.currency,
                        items=items,
                    ),
                )
            )

    approved = [p for p in payment_summaries if p.status == PaymentStatus.APPROVED]
    if approved:
        payment_summaries = approved

    slots = guest_slot_repo.list_by_invitation_id(invitation_id)
    couple_message = (invitation.metadata or {}).get("message")
    if isinstance(couple_message, str) and not couple_message.strip():
        couple_message = None

    return InvitationConfirmationResponse(
        invitation_id=invitation_id,
        event_id=invitation.event_id,
        guest_slots=[s.model_dump(mode="json") for s in slots],
        couple_message=couple_message if isinstance(couple_message, str) else None,
        payments=payment_summaries,
    )

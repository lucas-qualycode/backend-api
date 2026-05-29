from unittest.mock import MagicMock

from application.invitations.guest_payment import get_active_checkout
from domain.orders.entity import OrderQueryParams


def test_get_active_checkout_empty_has_no_pending_status():
    order_repo = MagicMock()
    payment_repo = MagicMock()
    order_repo.list.return_value = []

    result = get_active_checkout(
        "inv-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
    )

    order_repo.list.assert_called_once_with(OrderQueryParams(invitation_id="inv-1", limit=20))
    assert result.active is False
    assert result.has_approved_payment is False
    assert result.payment_id is None
    assert result.order_id is None
    assert result.payment_status is None
    assert result.next_action is None


def test_get_active_checkout_returns_latest_cancelled_payment():
    from domain.orders.entity import Order
    from domain.payments.entity import Payment, PaymentStatus

    order_repo = MagicMock()
    payment_repo = MagicMock()

    order = Order.model_validate(
        {
            "id": "ord-1",
            "user_id": "guest:inv-1",
            "invitation_id": "inv-1",
            "subtotal": 5000,
            "tax_amount": 0,
            "discount_amount": 0,
            "total_amount": 5000,
            "currency": "BRL",
            "status": "pending",
            "items": [],
            "expires_at": "2099-01-01T00:00:00Z",
            "created_at": "2026-01-02T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        },
    )
    payment = Payment.model_validate(
        {
            "id": "pay-cancelled",
            "order_id": "ord-1",
            "user_id": "guest:inv-1",
            "status": PaymentStatus.CANCELLED,
            "amount": 5000,
            "currency": "BRL",
            "payment_provider": "mercadopago",
            "payment_method": "pix",
            "created_at": "2026-01-02T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
            "metadata": {"provider_response": {"status": "cancelled"}},
        },
    )

    order_repo.list.return_value = [order]
    payment_repo.list.return_value = [payment]

    result = get_active_checkout(
        "inv-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
    )

    assert result.active is False
    assert result.payment_id == "pay-cancelled"
    assert result.order_id == "ord-1"
    assert result.payment_status == PaymentStatus.CANCELLED
    assert result.next_action == "failed"
    assert result.has_approved_payment is False

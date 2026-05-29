from unittest.mock import MagicMock

from application.invitations.guest_payment import get_active_checkout, get_guest_payment_status
from domain.orders.entity import Order, OrderQueryParams
from domain.payments.entity import Payment, PaymentQueryParams, PaymentStatus


def _payment(**overrides) -> Payment:
    base = {
        "id": "pay-1",
        "order_id": "ord-1",
        "user_id": "guest:inv-1",
        "amount": 1200,
        "currency": "BRL",
        "status": PaymentStatus.PENDING,
        "payment_provider": "mercadopago",
        "payment_method": "pix",
        "payment_provider_payment_id": "ORDTST01",
        "metadata": {
            "provider_response": {
                "id": "ORDTST01",
                "transactions": {
                    "payments": [
                        {
                            "status": "action_required",
                            "payment_method": {
                                "id": "pix",
                                "type": "bank_transfer",
                                "qr_code": "00020126580014br.gov.bcb.pix",
                                "qr_code_base64": "iVBOR",
                            },
                            "date_of_expiration": "2099-01-01T00:00:00.000Z",
                        }
                    ]
                },
            }
        },
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return Payment.model_validate(base)


def _order(**overrides) -> Order:
    base = {
        "id": "ord-1",
        "user_id": "guest:inv-1",
        "parent_id": "evt-1",
        "invitation_id": "inv-1",
        "subtotal": 1200,
        "tax_amount": 0,
        "discount_amount": 0,
        "total_amount": 1200,
        "currency": "BRL",
        "status": "pending",
        "items": [],
        "metadata": {},
        "expires_at": "2099-01-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return Order.model_validate(base)


def test_active_checkout_returns_pix_from_stored_provider_response():
    order_repo = MagicMock()
    payment_repo = MagicMock()
    order_repo.list.return_value = [_order()]
    payment_repo.list.return_value = [_payment()]

    result = get_active_checkout(
        "inv-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
    )

    assert result.active is True
    assert result.payment_method == "pix"
    assert result.next_action == "display_pix"
    assert result.pix is not None
    assert result.pix.copy_paste_code == "00020126580014br.gov.bcb.pix"
    assert result.pix.qr_code_base64 == "iVBOR"


def test_guest_payment_status_returns_pix_from_stored_provider_response():
    order_repo = MagicMock()
    payment_repo = MagicMock()
    order_repo.get_by_id.return_value = _order()
    payment_repo.get_by_id.return_value = _payment()

    result = get_guest_payment_status(
        "inv-1",
        "pay-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
    )

    assert result.payment_method == "pix"
    assert result.next_action == "display_pix"
    assert result.pix is not None
    assert result.pix.copy_paste_code == "00020126580014br.gov.bcb.pix"

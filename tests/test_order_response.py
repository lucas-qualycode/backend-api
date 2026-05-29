from domain.payments.entity import PaymentStatus
from infrastructure.mercadopago.order_response import map_provider_order_response


def test_map_pix_pending_orders_api_payment_method_fields():
    response = {
        "id": "ORD01",
        "status": "action_required",
        "transactions": {
            "payments": [
                {
                    "status": "action_required",
                    "status_detail": "pending_waiting_transfer",
                    "date_of_expiration": "2099-01-01T00:00:00.000Z",
                    "payment_method": {
                        "id": "pix",
                        "type": "bank_transfer",
                        "qr_code": "00020126580014br.gov.bcb.pix",
                        "qr_code_base64": "iVBOR",
                        "ticket_url": "https://www.mercadopago.com.br/payments/123/ticket",
                    },
                }
            ]
        },
    }
    mapped = map_provider_order_response(response)
    assert mapped.payment_status == PaymentStatus.PENDING
    assert mapped.payment_method == "pix"
    assert mapped.next_action == "display_pix"
    assert mapped.pix is not None
    assert mapped.pix.copy_paste_code == "00020126580014br.gov.bcb.pix"
    assert mapped.pix.qr_code_base64 == "iVBOR"
    assert mapped.pix.expires_at == "2099-01-01T00:00:00.000Z"


def test_map_pix_pending_response():
    response = {
        "id": "ORD01",
        "status": "action_required",
        "transactions": {
            "payments": [
                {
                    "status": "action_required",
                    "status_detail": "pending_waiting_transfer",
                    "payment_method": {"id": "pix", "type": "bank_transfer"},
                    "point_of_interaction": {
                        "transaction_data": {
                            "qr_code": "00020126580014br.gov.bcb.pix",
                            "qr_code_base64": "iVBOR",
                            "expiration_date": "2099-01-01T00:00:00.000Z",
                        }
                    },
                }
            ]
        },
    }
    mapped = map_provider_order_response(response)
    assert mapped.payment_status == PaymentStatus.PENDING
    assert mapped.payment_method == "pix"
    assert mapped.next_action == "display_pix"
    assert mapped.pix is not None
    assert mapped.pix.copy_paste_code == "00020126580014br.gov.bcb.pix"
    assert mapped.pix.qr_code_base64 == "iVBOR"


def test_map_card_approved_response():
    response = {
        "id": "ORD02",
        "transactions": {
            "payments": [
                {
                    "status": "approved",
                    "payment_method": {"id": "visa", "type": "credit_card"},
                }
            ]
        },
    }
    mapped = map_provider_order_response(response)
    assert mapped.payment_status == PaymentStatus.APPROVED
    assert mapped.payment_method == "card"
    assert mapped.next_action == "done"


def test_map_rejected_response():
    response = {
        "transactions": {
            "payments": [
                {
                    "status": "rejected",
                    "status_detail": "cc_rejected_insufficient_amount",
                    "payment_method": {"id": "visa", "type": "credit_card"},
                }
            ]
        },
    }
    mapped = map_provider_order_response(response)
    assert mapped.payment_status == PaymentStatus.FAILED
    assert mapped.next_action == "failed"
    assert mapped.failure is not None

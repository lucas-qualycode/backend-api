from unittest.mock import MagicMock, patch

import pytest

from application.invitations.checkout import (
    extract_payer_email,
    guest_user_id,
    process_invitation_checkout,
)
from application.orders.checkout_validation import (
    assert_total_cents_matches,
    validate_and_build_order_items,
)
from application.orders.schemas import InvitationCheckoutRequest, OrderItemInput
from domain.invitations.entity import Invitation, InvitationDestinationType, InvitationStatus
from domain.orders.entity import Order
from domain.payments.entity import Payment, PaymentStatus
from domain.products.entity import Product
from domain.products.types import ProductType
from infrastructure.mercadopago.client import MercadoPagoApiError
from infrastructure.persistence.firestore_checkout_intents import FirestoreCheckoutIntentRepository
from utils.errors import ValidationError


def _invitation() -> Invitation:
    return Invitation(
        id="inv-1",
        event_id="evt-1",
        inviter_id="u1",
        name="Test",
        ticket_id="t1",
        destination="d@e.com",
        destination_type=InvitationDestinationType.EMAIL,
        status=InvitationStatus.CREATED,
        expires_at="2099-01-01T00:00:00Z",
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        metadata={},
    )


def _product(product_id: str = "p1", value: int = 1000) -> Product:
    return Product(
        id=product_id,
        name="Ticket",
        description="",
        parent_id="evt-1",
        type=ProductType.TICKET,
        user_id="u1",
        is_free=False,
        value=value,
        quantity=100,
        max_per_user=10,
        active=True,
        deleted=False,
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        created_by="u1",
        last_updated_by="u1",
    )


class _ProductRepo:
    def __init__(self, products: dict[str, Product]) -> None:
        self._products = products

    def get_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)


class _OrderRepo:
    def __init__(self) -> None:
        self.created: list[Order] = []

    def create(self, order: Order) -> Order:
        self.created.append(order)
        return order

    def update(self, id: str, order: Order) -> Order:
        for i, o in enumerate(self.created):
            if o.id == id:
                self.created[i] = order
                return order
        return order


class _PaymentRepo:
    def __init__(self) -> None:
        self.created: list[Payment] = []
        self.updates: list[Payment] = []

    def create(self, payment: Payment) -> Payment:
        self.created.append(payment)
        return payment

    def update(self, id: str, payment: Payment) -> Payment:
        self.updates.append(payment)
        for i, p in enumerate(self.created):
            if p.id == id:
                self.created[i] = payment
        return payment


class _CheckoutIntentRepo:
    STATUS_PROCESSING = FirestoreCheckoutIntentRepository.STATUS_PROCESSING
    STATUS_COMPLETED = FirestoreCheckoutIntentRepository.STATUS_COMPLETED

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    @staticmethod
    def _key(invitation_id: str, idempotency_key: str) -> str:
        return FirestoreCheckoutIntentRepository.document_id(invitation_id, idempotency_key)

    def get(self, invitation_id: str, idempotency_key: str) -> dict | None:
        return self._store.get(self._key(invitation_id, idempotency_key))

    def try_start_processing(self, invitation_id: str, idempotency_key: str) -> bool:
        key = self._key(invitation_id, idempotency_key)
        if key in self._store:
            return False
        self._store[key] = {
            "status": FirestoreCheckoutIntentRepository.STATUS_PROCESSING,
        }
        return True

    def retry_after_failure(self, invitation_id: str, idempotency_key: str) -> bool:
        key = self._key(invitation_id, idempotency_key)
        row = self._store.get(key)
        if not row or row.get("status") != "failed":
            return False
        row["status"] = FirestoreCheckoutIntentRepository.STATUS_PROCESSING
        return True

    def complete(self, invitation_id, idempotency_key, **kwargs) -> None:
        key = self._key(invitation_id, idempotency_key)
        self._store[key] = {
            "status": FirestoreCheckoutIntentRepository.STATUS_COMPLETED,
            **kwargs,
        }

    def fail(self, invitation_id, idempotency_key, *, error: str) -> None:
        key = self._key(invitation_id, idempotency_key)
        self._store[key] = {"status": "failed", "error": error}


def _checkout_request(**overrides) -> InvitationCheckoutRequest:
    base = {
        "parent_id": "evt-1",
        "invitation_id": "inv-1",
        "items": [
            {
                "product_id": "p1",
                "quantity": 1,
                "unit_price_cents": 1000,
                "total_price_cents": 1000,
            }
        ],
        "total_cents": 1000,
        "currency": "BRL",
        "payment_provider": "mercadopago",
        "provider_checkout": {
            "type": "online",
            "total_amount": "10.00",
            "payer": {"email": "guest@example.com"},
            "transactions": {"payments": [{"payment_method": {"id": "pix"}}]},
        },
    }
    base.update(overrides)
    return InvitationCheckoutRequest.model_validate(base)


def test_validate_rejects_tampered_unit_price():
    repo = _ProductRepo({"p1": _product()})
    items = [
        OrderItemInput(
            product_id="p1",
            quantity=1,
            unit_price=500,
            total_price_cents=500,
        )
    ]
    with pytest.raises(ValidationError, match="Invalid unit price"):
        validate_and_build_order_items(repo, items, "evt-1")


def test_validate_rejects_wrong_parent_event():
    repo = _ProductRepo({"p1": _product()})
    items = [OrderItemInput(product_id="p1", quantity=1, unit_price_cents=1000)]
    with pytest.raises(ValidationError, match="does not belong"):
        validate_and_build_order_items(repo, items, "other-event")


def test_assert_total_cents_mismatch():
    with pytest.raises(ValidationError, match="total_cents"):
        assert_total_cents_matches(1000, 999)


def test_extract_payer_email():
    assert extract_payer_email({"payer": {"email": "a@b.com"}}) == "a@b.com"
    assert extract_payer_email({}) is None


def test_guest_user_id():
    assert guest_user_id("inv-1") == "guest:inv-1"


@patch("application.invitations.checkout.mp_client.create_order")
def test_checkout_success_creates_order_and_payment(mock_mp):
    mock_mp.return_value = {"id": "mp-order-1"}
    order_repo = _OrderRepo()
    payment_repo = _PaymentRepo()
    intent_repo = _CheckoutIntentRepo()
    product_repo = _ProductRepo({"p1": _product()})

    result = process_invitation_checkout(
        _invitation(),
        _checkout_request(),
        idempotency_key="key-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
        product_repo=product_repo,
        checkout_intent_repo=intent_repo,
        now="2026-01-01T00:00:00Z",
    )

    assert result.idempotent_replay is False
    assert len(order_repo.created) == 1
    assert order_repo.created[0].user_id == "guest:inv-1"
    assert order_repo.created[0].metadata.get("payer_email") == "guest@example.com"
    assert len(payment_repo.created) == 1
    assert payment_repo.created[0].status == PaymentStatus.PENDING
    assert result.payment_provider_payment_id == "mp-order-1"
    assert payment_repo.updates[-1].metadata.get("provider_response") == {"id": "mp-order-1"}
    mock_mp.assert_called_once()


@patch("application.invitations.checkout.mp_client.create_order")
def test_checkout_idempotent_replay(mock_mp):
    mock_mp.return_value = {"id": "mp-order-1"}
    order_repo = _OrderRepo()
    payment_repo = _PaymentRepo()
    intent_repo = _CheckoutIntentRepo()
    product_repo = _ProductRepo({"p1": _product()})

    first = process_invitation_checkout(
        _invitation(),
        _checkout_request(),
        idempotency_key="key-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
        product_repo=product_repo,
        checkout_intent_repo=intent_repo,
        now="2026-01-01T00:00:00Z",
    )
    second = process_invitation_checkout(
        _invitation(),
        _checkout_request(),
        idempotency_key="key-1",
        order_repo=order_repo,
        payment_repo=payment_repo,
        product_repo=product_repo,
        checkout_intent_repo=intent_repo,
        now="2026-01-01T00:00:00Z",
    )

    assert first.order_id == second.order_id
    assert second.idempotent_replay is True
    assert len(order_repo.created) == 1
    assert mock_mp.call_count == 1


@patch("application.invitations.checkout.mp_client.create_order")
def test_checkout_rejects_parent_id_mismatch(mock_mp):
    with pytest.raises(ValidationError, match="parent_id"):
        process_invitation_checkout(
            _invitation(),
            _checkout_request(parent_id="wrong"),
            idempotency_key="key-2",
            order_repo=_OrderRepo(),
            payment_repo=_PaymentRepo(),
            product_repo=_ProductRepo({"p1": _product()}),
            checkout_intent_repo=_CheckoutIntentRepo(),
            now="2026-01-01T00:00:00Z",
        )
    mock_mp.assert_not_called()


@patch("application.invitations.checkout.mp_client.create_order", side_effect=MercadoPagoApiError("fail", 400))
def test_checkout_marks_payment_failed_on_mp_error(mock_mp):
    order_repo = _OrderRepo()
    payment_repo = _PaymentRepo()
    intent_repo = _CheckoutIntentRepo()
    product_repo = _ProductRepo({"p1": _product()})

    with pytest.raises(MercadoPagoApiError):
        process_invitation_checkout(
            _invitation(),
            _checkout_request(),
            idempotency_key="key-3",
            order_repo=order_repo,
            payment_repo=payment_repo,
            product_repo=product_repo,
            checkout_intent_repo=intent_repo,
            now="2026-01-01T00:00:00Z",
        )

    assert payment_repo.updates[-1].status == PaymentStatus.FAILED
    assert intent_repo.get("inv-1", "key-3")["status"] == "failed"

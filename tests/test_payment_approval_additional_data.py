import importlib
approval_module = importlib.import_module("application.payments.process_payment_approval")
from domain.orders.entity import Order, OrderItem
from domain.payments.entity import Payment
from domain.products.entity import Product
from domain.products.types import ProductType


class _Repo:
    def __init__(self, rows: dict):
        self.rows = rows

    def get_by_id(self, id: str):
        return self.rows.get(id)


class _InvitationRepo:
    def get_by_id(self, id: str):
        return None


def _payment() -> Payment:
    return Payment(
        id="pay1",
        order_id="ord1",
        user_id="user1",
        amount=1000,
        currency="BRL",
        status="APPROVED",
        payment_provider="mercadopago",
        created_at="t",
        updated_at="t",
        metadata={},
    )


def _product() -> Product:
    return Product(
        id="prod1",
        name="Ticket",
        description="d",
        parent_id="event1",
        parent_type="EVENT",
        type=ProductType.TICKET,
        user_id="user1",
        is_free=False,
        value=500,
        quantity=10,
        max_per_user=2,
        request_additional_info=True,
        additional_info_fields=[],
        active=True,
        deleted=False,
        created_at="t",
        updated_at="t",
        created_by="user1",
        last_updated_by="user1",
        metadata={},
    )


def test_process_payment_approval_prefers_order_item_additional_data(monkeypatch) -> None:
    order = Order(
        id="ord1",
        user_id="user1",
        parent_id="event1",
        items=[
            OrderItem(
                id="i1",
                product_id="prod1",
                quantity=1,
                unit_price=500,
                total_price=500,
                currency="BRL",
                metadata={"additional_data": [{"name": "legacy"}]},
                additional_data=[{"name": "new"}],
            )
        ],
        subtotal=500,
        tax_amount=0,
        discount_amount=0,
        total_amount=500,
        currency="BRL",
        status="CREATED",
        created_at="t",
        updated_at="t",
        expires_at="t",
        metadata={},
    )
    captured: list[dict] = []

    def _fake_create_user_product(repo, data, now):
        captured.append(data.additional_data)
        return None

    monkeypatch.setattr(approval_module, "create_user_product", _fake_create_user_product)
    approval_module.process_payment_approval(
        payment_id="pay1",
        payment_repo=_Repo({"pay1": _payment()}),
        order_repo=_Repo({"ord1": order}),
        product_repo=_Repo({"prod1": _product()}),
        user_product_repo=object(),
        invitation_repo=_InvitationRepo(),
    )
    assert captured == [{"name": "new"}]


def test_process_payment_approval_falls_back_to_legacy_metadata(monkeypatch) -> None:
    order = Order(
        id="ord1",
        user_id="user1",
        parent_id="event1",
        items=[
            OrderItem(
                id="i1",
                product_id="prod1",
                quantity=1,
                unit_price=500,
                total_price=500,
                currency="BRL",
                metadata={"additional_data": [{"name": "legacy"}]},
                additional_data=[],
            )
        ],
        subtotal=500,
        tax_amount=0,
        discount_amount=0,
        total_amount=500,
        currency="BRL",
        status="CREATED",
        created_at="t",
        updated_at="t",
        expires_at="t",
        metadata={},
    )
    captured: list[dict] = []

    def _fake_create_user_product(repo, data, now):
        captured.append(data.additional_data)
        return None

    monkeypatch.setattr(approval_module, "create_user_product", _fake_create_user_product)
    approval_module.process_payment_approval(
        payment_id="pay1",
        payment_repo=_Repo({"pay1": _payment()}),
        order_repo=_Repo({"ord1": order}),
        product_repo=_Repo({"prod1": _product()}),
        user_product_repo=object(),
        invitation_repo=_InvitationRepo(),
    )
    assert captured == [{"name": "legacy"}]

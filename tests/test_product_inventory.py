import pytest

from application.products.inventory_build import (
    inventory_deactivate_update_dict,
    inventory_update_dict_for_product,
    new_inventory_item_for_product,
)
from application.products.validation import validate_product_create, validate_product_state
from domain.inventory.entity import InventoryItem
from domain.products.entity import Product
from domain.products.types import (
    InventoryProductType,
    ProductType,
    inventory_document_id,
    inventory_product_type_field,
)
from application.products.schemas import CreateProductInput
from utils.errors import ValidationError


def test_inventory_document_id() -> None:
    assert inventory_document_id("abc-1") == "PRODUCT_abc-1"


def test_inventory_product_type_field() -> None:
    assert inventory_product_type_field(None) == InventoryProductType.PRODUCT
    assert inventory_product_type_field("TICKET") == InventoryProductType.TICKET
    assert inventory_product_type_field(ProductType.MERCH) == InventoryProductType.PRODUCT
    assert inventory_product_type_field(ProductType.TICKET) == InventoryProductType.TICKET
    assert inventory_product_type_field("OTHER") == InventoryProductType.PRODUCT


def test_new_inventory_item_for_product() -> None:
    p = Product(
        id="p1",
        name="n",
        description="d",
        parent_id="e1",
        parent_type="EVENT",
        type=ProductType.TICKET,
        user_id="u1",
        is_free=False,
        value=1000,
        quantity=50,
        max_per_user=5,
        request_additional_info=False,
        additional_info_fields=[],
        active=True,
        deleted=False,
        created_at="t0",
        updated_at="t0",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )
    inv = new_inventory_item_for_product(p, "t1", "BRL")
    assert inv.id == "PRODUCT_p1"
    assert inv.product_type == "TICKET"
    assert inv.available_quantity == 50
    assert inv.total_quantity == 50
    assert inv.reserved_quantity == 0
    assert inv.price == 1000


def test_inventory_update_respects_reserved() -> None:
    p = Product(
        id="p1",
        name="n",
        description="d",
        parent_id=None,
        parent_type=None,
        type=ProductType.MERCH,
        user_id="u1",
        is_free=False,
        value=100,
        quantity=10,
        max_per_user=1,
        request_additional_info=False,
        additional_info_fields=[],
        active=True,
        deleted=False,
        created_at="t0",
        updated_at="t1",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )
    current = InventoryItem(
        id="PRODUCT_p1",
        product_type="PRODUCT",
        product_id="p1",
        available_quantity=3,
        reserved_quantity=7,
        total_quantity=10,
        price=100,
        currency="BRL",
        created_at="t0",
        updated_at="t0",
        metadata={},
    )
    p2 = p.model_copy(update={"quantity": 15})
    upd = inventory_update_dict_for_product(p2, current, "t2")
    assert upd["total_quantity"] == 15
    assert upd["available_quantity"] == 8


def test_inventory_update_reserved_exceeds_new_total() -> None:
    p = Product(
        id="p1",
        name="n",
        description="d",
        parent_id=None,
        parent_type=None,
        type=ProductType.MERCH,
        user_id="u1",
        is_free=False,
        value=100,
        quantity=5,
        max_per_user=1,
        request_additional_info=False,
        additional_info_fields=[],
        active=True,
        deleted=False,
        created_at="t0",
        updated_at="t1",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )
    current = InventoryItem(
        id="PRODUCT_p1",
        product_type="PRODUCT",
        product_id="p1",
        available_quantity=0,
        reserved_quantity=10,
        total_quantity=10,
        price=100,
        currency="BRL",
        created_at="t0",
        updated_at="t0",
        metadata={},
    )
    upd = inventory_update_dict_for_product(p, current, "t2")
    assert upd["available_quantity"] == 0


def test_inventory_deactivate_update_dict() -> None:
    d = inventory_deactivate_update_dict("now", {"a": 1})
    assert d["available_quantity"] == 0
    assert d["updated_at"] == "now"
    assert d["metadata"]["deleted"] is True


def test_validate_product_create_free() -> None:
    validate_product_create(
        CreateProductInput(
            name="x",
            description="y",
            is_free=True,
            value=0,
            quantity=1,
            max_per_user=1,
            request_additional_info=False,
        )
    )


def test_validate_product_create_paid() -> None:
    validate_product_create(
        CreateProductInput(
            name="x",
            description="y",
            is_free=False,
            value=100,
            quantity=2,
            max_per_user=2,
            request_additional_info=False,
        )
    )


def test_validate_product_create_rejects_free_with_value() -> None:
    with pytest.raises(ValidationError):
        validate_product_create(
            CreateProductInput(
                name="x",
                description="y",
                is_free=True,
                value=10,
                quantity=1,
                max_per_user=1,
                request_additional_info=False,
            )
        )


def test_validate_product_state() -> None:
    p = Product(
        id="p1",
        name="n",
        description="d",
        parent_id=None,
        parent_type=None,
        type=ProductType.MERCH,
        user_id="u1",
        is_free=False,
        value=1,
        quantity=1,
        max_per_user=1,
        request_additional_info=False,
        active=True,
        deleted=False,
        created_at="t",
        updated_at="t",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )
    validate_product_state(p)

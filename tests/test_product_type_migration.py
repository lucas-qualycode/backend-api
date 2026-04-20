from domain.products.entity import Product
from domain.products.field_groups import (
    PRODUCT_CATALOG_FIELD_NAMES,
    PRODUCT_COMMERCE_FIELD_NAMES,
    PRODUCT_STOCK_FIELD_NAMES,
)
from domain.products.types import ProductType


def _minimal_product_dict(**overrides):
    base = {
        "id": "p1",
        "name": "n",
        "description": "d",
        "user_id": "u1",
        "is_free": False,
        "value": 100,
        "quantity": 1,
        "max_per_user": 1,
        "request_additional_info": False,
        "active": True,
        "deleted": False,
        "created_at": "t",
        "updated_at": "t",
        "created_by": "u1",
        "last_updated_by": "u1",
        "metadata": {},
    }
    base.update(overrides)
    return base


def test_product_validate_defaults_missing_type_to_merch() -> None:
    d = {k: v for k, v in _minimal_product_dict().items() if k != "type"}
    p = Product.model_validate(d)
    assert p.type == ProductType.MERCH


def test_product_validate_maps_unknown_type_to_merch() -> None:
    p = Product.model_validate(_minimal_product_dict(type="LEGACY_OTHER"))
    assert p.type == ProductType.MERCH


def test_product_validate_keeps_ticket() -> None:
    p = Product.model_validate(_minimal_product_dict(type="TICKET"))
    assert p.type == ProductType.TICKET


def test_field_groups_partition_product_fields() -> None:
    assert "type" in PRODUCT_CATALOG_FIELD_NAMES
    assert "value" in PRODUCT_COMMERCE_FIELD_NAMES
    assert "quantity" in PRODUCT_STOCK_FIELD_NAMES

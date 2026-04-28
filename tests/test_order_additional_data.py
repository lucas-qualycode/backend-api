import pytest

from application.orders.schemas import OrderItemInput
from application.orders.validate_additional_data import validate_order_items_additional_data
from domain.field_definitions.entity import FieldDefinition, FieldType
from domain.products.entity import Product
from domain.products.types import ProductType
from domain.products.exceptions import ProductNotFoundError
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError
from utils.errors import ValidationError


def _product(
    pid: str,
    refs: list[dict] | None = None,
) -> Product:
    return Product(
        id=pid,
        name="n",
        description="d",
        parent_id=None,
        parent_type=None,
        type=ProductType.MERCH,
        user_id="u1",
        is_free=False,
        value=100,
        quantity=99,
        max_per_user=5,
        additional_info_fields=refs or [],
        active=True,
        deleted=False,
        created_at="t",
        updated_at="t",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )


def _field(fid: str, key: str, field_type: str = FieldType.TEXT, **kwargs) -> FieldDefinition:
    return FieldDefinition(
        id=fid,
        key=key,
        label=key,
        description=None,
        field_type=field_type,
        required_default=kwargs.get("required_default", False),
        format=kwargs.get("format"),
        min_length=kwargs.get("min_length"),
        max_length=kwargs.get("max_length"),
        minimum=kwargs.get("minimum"),
        maximum=kwargs.get("maximum"),
        options=kwargs.get("options", []),
        active=True,
        deleted=False,
        created_at="t",
        updated_at="t",
        created_by="u1",
        last_updated_by="u1",
    )


class _FakeProductRepo:
    def __init__(self, products: dict[str, Product]) -> None:
        self._p = products

    def get_by_id(self, id: str) -> Product | None:
        return self._p.get(id)


class _FakeFieldRepo:
    def __init__(self, rows: dict[str, FieldDefinition]) -> None:
        self._t = rows

    def get_by_id(self, id: str) -> FieldDefinition | None:
        return self._t.get(id)


def test_field_refs_path_validates_each_unit() -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "full_name", min_length=1, max_length=50)}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=2,
            unit_price=10,
            currency="BRL",
            additional_data=[{"full_name": "A"}, {"full_name": "B"}],
        )
    ]
    validate_order_items_additional_data(
        _FakeProductRepo(products), _FakeFieldRepo(fields), items
    )


def test_field_refs_wrong_length() -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "full_name")}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=2,
            unit_price=10,
            currency="BRL",
            additional_data=[{"full_name": "A"}],
        )
    ]
    with pytest.raises(ValidationError, match="must have 2 entries"):
        validate_order_items_additional_data(
            _FakeProductRepo(products), _FakeFieldRepo(fields), items
        )


def test_no_fields_rejects_additional_data() -> None:
    pid = "p1"
    products = {pid: _product(pid)}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            additional_data=[{"x": 1}],
        )
    ]
    with pytest.raises(ValidationError, match="does not collect"):
        validate_order_items_additional_data(
            _FakeProductRepo(products), _FakeFieldRepo({}), items
        )


def test_missing_product() -> None:
    items = [
        OrderItemInput(
            product_id="missing",
            quantity=1,
            unit_price=10,
            currency="BRL",
            metadata={},
        )
    ]
    with pytest.raises(ProductNotFoundError):
        validate_order_items_additional_data(
            _FakeProductRepo({}), _FakeFieldRepo({}), items
        )


def test_field_definition_not_found() -> None:
    pid = "p1"
    products = {pid: _product(pid, refs=[{"field_id": "ghost", "required": True}])}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            additional_data=[{"full_name": "x"}],
        )
    ]
    with pytest.raises(FieldDefinitionNotFoundError):
        validate_order_items_additional_data(
            _FakeProductRepo(products), _FakeFieldRepo({}), items
        )


def test_ref_override_can_make_field_required() -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "full_name", required_default=False)}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            additional_data=[{}],
        )
    ]
    with pytest.raises(ValidationError, match="Missing required field"):
        validate_order_items_additional_data(
            _FakeProductRepo(products), _FakeFieldRepo(fields), items
        )


def test_legacy_metadata_additional_data_is_accepted() -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "full_name")}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            metadata={"additional_data": [{"full_name": "Legacy"}]},
        )
    ]
    validate_order_items_additional_data(
        _FakeProductRepo(products), _FakeFieldRepo(fields), items
    )


@pytest.mark.parametrize(
    ("field_format", "value"),
    [
        ("email", "user@example.com"),
        ("url", "https://example.com/path"),
        ("date_iso", "2026-04-21"),
        ("time_iso", "13:45:00"),
        ("datetime_iso", "2026-04-21T13:45:00Z"),
    ],
)
def test_text_format_valid_values(field_format: str, value: str) -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "contact", format=field_format)}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            additional_data=[{"contact": value}],
        )
    ]
    validate_order_items_additional_data(
        _FakeProductRepo(products), _FakeFieldRepo(fields), items
    )


@pytest.mark.parametrize(
    ("field_format", "value", "message"),
    [
        ("email", "invalid-email", "valid email"),
        ("url", "ftp://example.com", "valid URL"),
        ("date_iso", "21-04-2026", "valid ISO date"),
        ("time_iso", "25:70", "valid ISO time"),
        ("datetime_iso", "2026/04/21 13:45", "valid ISO datetime"),
    ],
)
def test_text_format_rejects_invalid_values(
    field_format: str, value: str, message: str
) -> None:
    pid, fid = "p1", "f1"
    products = {pid: _product(pid, refs=[{"field_id": fid, "required": True}])}
    fields = {fid: _field(fid, "contact", format=field_format)}
    items = [
        OrderItemInput(
            product_id=pid,
            quantity=1,
            unit_price=10,
            currency="BRL",
            additional_data=[{"contact": value}],
        )
    ]
    with pytest.raises(ValidationError, match=message):
        validate_order_items_additional_data(
            _FakeProductRepo(products), _FakeFieldRepo(fields), items
        )

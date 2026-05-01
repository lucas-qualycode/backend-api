from types import SimpleNamespace

import pytest

from application.invitations.schemas import CreateInvitationGuestSlotInput
from application.invitations.validate_guest_slots import validate_guest_slots_for_create
from domain.field_definitions.entity import FieldDefinition
from domain.products.entity import Product
from domain.products.types import ProductType
from utils.errors import ValidationError


class _ProductRepo:
    def __init__(self, products: dict[str, Product]) -> None:
        self._products = products

    def get_by_id(self, id: str) -> Product | None:
        return self._products.get(id)


class _FieldDefRepo:
    def __init__(self, rows: dict[str, FieldDefinition] | None = None) -> None:
        self._rows = rows or {}

    def get_by_id(self, id: str) -> FieldDefinition | None:
        return self._rows.get(id)


def _field_def(fid: str) -> FieldDefinition:
    return FieldDefinition(
        id=fid,
        key=fid,
        label=fid,
        field_type="text",
        active=True,
        deleted=False,
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        created_by="u1",
        last_updated_by="u1",
    )


def _ticket_with_fields(event_id: str, field_ids: list[str], max_per_user: int = 1) -> Product:
    from domain.products.entity import ProductAdditionalInfoFieldRef

    refs = [
        ProductAdditionalInfoFieldRef(field_id=fid, label=None, required=None, order=i, active=True)
        for i, fid in enumerate(field_ids)
    ]
    return Product(
        id="t1",
        name="GA",
        description="d",
        parent_id=event_id,
        parent_type="EVENT",
        type=ProductType.TICKET,
        user_id="u1",
        is_free=False,
        value=100,
        quantity=10,
        max_per_user=max_per_user,
        additional_info_fields=refs,
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        created_by="u1",
        last_updated_by="u1",
    )


def test_validate_accepts_two_guests_different_fields():
    p = _ticket_with_fields("e1", ["f_full", "f_age"], max_per_user=2)
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo()
    guests = [
        CreateInvitationGuestSlotInput(first_name="Ana", required_field_ids=["f_full"]),
        CreateInvitationGuestSlotInput(first_name="Beto", required_field_ids=["f_full", "f_age"]),
    ]
    validate_guest_slots_for_create(repo, field_repo, "t1", 2, guests)


def test_validate_accepts_empty_first_names_when_slot_count_allows():
    p = _ticket_with_fields("e1", ["f_full"], max_per_user=3)
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo()
    validate_guest_slots_for_create(
        repo,
        field_repo,
        "t1",
        3,
        [CreateInvitationGuestSlotInput(first_name="", required_field_ids=[])],
    )


def test_validate_rejects_unknown_field_id():
    p = _ticket_with_fields("e1", ["f_full"])
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo()
    guests = [CreateInvitationGuestSlotInput(first_name="Ana", required_field_ids=["unknown"])]
    with pytest.raises(ValidationError, match="unknown field_id"):
        validate_guest_slots_for_create(repo, field_repo, "t1", 1, guests)


def test_validate_accepts_field_from_catalog_not_on_ticket():
    p = _ticket_with_fields("e1", ["f_full"])
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo({"f_extra": _field_def("f_extra")})
    guests = [CreateInvitationGuestSlotInput(first_name="Ana", required_field_ids=["f_extra"])]
    validate_guest_slots_for_create(repo, field_repo, "t1", 1, guests)


def test_validate_rejects_field_ids_without_ticket():
    repo = _ProductRepo({})
    field_repo = _FieldDefRepo()
    guests = [CreateInvitationGuestSlotInput(first_name="Ana", required_field_ids=["f1"])]
    with pytest.raises(ValidationError, match="ticket_id"):
        validate_guest_slots_for_create(repo, field_repo, None, 0, guests)


def test_validate_rejects_guest_slot_count_without_ticket():
    repo = _ProductRepo({})
    field_repo = _FieldDefRepo()
    with pytest.raises(ValidationError, match="guest_slot_count requires ticket_id"):
        validate_guest_slots_for_create(repo, field_repo, None, 2, [])


def test_validate_rejects_more_slots_than_ticket_max_per_user():
    p = _ticket_with_fields("e1", ["f_full"], max_per_user=1)
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo()
    with pytest.raises(ValidationError, match="At most 1 guest slot"):
        validate_guest_slots_for_create(repo, field_repo, "t1", 2, [])


def test_validate_rejects_more_detail_rows_than_slot_count():
    p = _ticket_with_fields("e1", ["f_full"], max_per_user=5)
    repo = _ProductRepo({"t1": p})
    field_repo = _FieldDefRepo()
    guests = [
        CreateInvitationGuestSlotInput(first_name="A", required_field_ids=[]),
        CreateInvitationGuestSlotInput(first_name="B", required_field_ids=[]),
    ]
    with pytest.raises(ValidationError, match="Too many guest detail rows"):
        validate_guest_slots_for_create(repo, field_repo, "t1", 1, guests)

import pytest

from application.invitations.validate_invitation_ticket import validate_invitation_ticket_for_event
from domain.products.entity import Product
from domain.products.types import ProductType
from utils.errors import ValidationError


class _ProductRepo:
    def __init__(self, products: dict[str, Product]) -> None:
        self._products = products

    def get_by_id(self, id: str) -> Product | None:
        return self._products.get(id)


def _ticket(event_id: str, pid: str = "t1") -> Product:
    return Product(
        id=pid,
        name="GA",
        description="d",
        parent_id=event_id,
        parent_type="EVENT",
        type=ProductType.TICKET,
        user_id="u1",
        is_free=False,
        value=100,
        quantity=10,
        max_per_user=1,
        additional_info_fields=[],
        active=True,
        deleted=False,
        created_at="t",
        updated_at="t",
        created_by="u1",
        last_updated_by="u1",
        metadata={},
    )


def test_validate_accepts_ticket_for_event() -> None:
    repo = _ProductRepo({"t1": _ticket("e1")})
    validate_invitation_ticket_for_event(repo, "t1", "e1")


def test_validate_rejects_missing_product() -> None:
    repo = _ProductRepo({})
    with pytest.raises(ValidationError, match="not found"):
        validate_invitation_ticket_for_event(repo, "t1", "e1")


def test_validate_rejects_wrong_event() -> None:
    repo = _ProductRepo({"t1": _ticket("e-other")})
    with pytest.raises(ValidationError, match="does not belong"):
        validate_invitation_ticket_for_event(repo, "t1", "e1")


def test_validate_rejects_merch() -> None:
    p = _ticket("e1")
    merch = p.model_copy(update={"type": ProductType.MERCH})
    repo = _ProductRepo({"m1": merch})
    with pytest.raises(ValidationError, match="not a ticket"):
        validate_invitation_ticket_for_event(repo, "m1", "e1")

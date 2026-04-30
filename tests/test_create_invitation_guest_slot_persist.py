from unittest.mock import MagicMock, patch

import pytest

from application.invitations.create_invitation import create_invitation
from application.invitations.schemas import CreateInvitationInput
from application.invitations.validate_guest_slots import validate_guest_slots_for_create
from domain.products.entity import Product
from domain.products.types import ProductType
from utils.errors import ValidationError


def _ticket(event_id: str, max_per_user: int = 5) -> Product:
    from domain.products.entity import ProductAdditionalInfoFieldRef

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
        additional_info_fields=[
            ProductAdditionalInfoFieldRef(field_id="f1", label=None, required=None, order=0, active=True)
        ],
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        created_by="u1",
        last_updated_by="u1",
    )


@patch("application.invitations.create_invitation.run_create_invitation_with_guest_slots")
def test_create_invitation_persists_only_filled_guest_rows(mock_tx: MagicMock) -> None:
    p = _ticket("e1")
    product_repo = MagicMock()
    product_repo.get_by_id.return_value = p
    repo = MagicMock()
    db = MagicMock()
    data = CreateInvitationInput(
        event_id="e1",
        inviter_id="u1",
        name="Inv",
        destination="+5511999999999",
        destination_type="WHATSAPP",
        expires_at="2030-01-01T00:00:00Z",
        ticket_id="t1",
        guest_slot_count=3,
        guests=[
            {"first_name": "", "required_field_ids": []},
            {"first_name": "  Ana  ", "required_field_ids": []},
            {"first_name": "", "required_field_ids": []},
        ],
    )
    invitation = create_invitation(db, repo, product_repo, data, "now")
    mock_tx.assert_called_once()
    passed_inv, slots = mock_tx.call_args[0][1], mock_tx.call_args[0][2]
    assert invitation.guest_slot_count == 3
    assert passed_inv.guest_slot_count == 3
    assert len(slots) == 1
    assert slots[0].first_name == "Ana"


def test_validate_rejects_all_empty_rows_when_exceeding_slot_count_via_row_length() -> None:
    p = _ticket("e1", max_per_user=3)
    repo = MagicMock()
    repo.get_by_id.return_value = p
    from application.invitations.schemas import CreateInvitationGuestSlotInput

    guests = [
        CreateInvitationGuestSlotInput(first_name="", required_field_ids=[]),
        CreateInvitationGuestSlotInput(first_name="", required_field_ids=[]),
        CreateInvitationGuestSlotInput(first_name="", required_field_ids=[]),
    ]
    with pytest.raises(ValidationError, match="Too many guest detail rows"):
        validate_guest_slots_for_create(repo, "t1", 2, guests)

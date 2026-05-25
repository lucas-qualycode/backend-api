from unittest.mock import MagicMock, patch

import pytest

from application.invitations.schemas import SubmitGuestInvitationInput, SubmitGuestSlotInput
from application.invitations.submit_guest_invitation import (
    GUEST_MESSAGE_METADATA_KEY,
    submit_guest_invitation,
)
from domain.invitation_guest_slots.entity import InvitationGuestSlot, InvitationGuestSlotStatus
from domain.invitations.entity import Invitation, InvitationDestinationType, InvitationStatus
from utils.errors import ValidationError


def _invitation(
    *,
    guest_slot_count: int = 5,
    ticket_id: str | None = "t1",
) -> Invitation:
    return Invitation(
        id="inv-1",
        event_id="e1",
        inviter_id="u1",
        name="Test",
        ticket_id=ticket_id,
        destination="d@e.com",
        destination_type=InvitationDestinationType.EMAIL,
        status=InvitationStatus.CREATED,
        expires_at="2099-01-01T00:00:00Z",
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        guest_slot_count=guest_slot_count,
        metadata={},
    )


def _existing_slot(slot_id: str, first_name: str = "Ana") -> InvitationGuestSlot:
    return InvitationGuestSlot(
        id=slot_id,
        invitation_id="inv-1",
        first_name=first_name,
        required_field_ids=["f_full"],
        field_values={},
        attending=True,
        status=InvitationGuestSlotStatus.PENDING,
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
    )


class _InvitationRepo:
    def __init__(self, invitation: Invitation) -> None:
        self._invitation = invitation

    def get_by_id(self, id: str) -> Invitation | None:
        if id != self._invitation.id:
            return None
        return self._invitation

    def update(self, id: str, invitation: Invitation) -> Invitation:
        self._invitation = invitation
        return invitation


class _GuestSlotRepo:
    def __init__(self, slots: list[InvitationGuestSlot]) -> None:
        self._slots = list(slots)
        self.last_written: list[InvitationGuestSlot] = []

    def list_by_invitation_id(self, invitation_id: str) -> list[InvitationGuestSlot]:
        return list(self._slots)

    def set_written(self, slots: list[InvitationGuestSlot]) -> None:
        self._slots = list(slots)
        self.last_written = list(slots)


@patch("application.invitations.submit_guest_invitation.run_update_invitation_with_guest_slots")
def test_submit_guests_updates_existing_and_creates_new(mock_tx):
    inv = _invitation()
    repo = _InvitationRepo(inv)
    guest_repo = _GuestSlotRepo(
        [
            _existing_slot("s1", "Ana"),
            _existing_slot("s2", "Beto"),
            _existing_slot("s3", "Carla"),
        ]
    )

    def capture_tx(db, invitation_id, invitation, slots):
        guest_repo.set_written(slots)

    mock_tx.side_effect = capture_tx

    guests = [
        SubmitGuestSlotInput(
            id="s1",
            first_name="Ana",
            required_field_ids=["f_full"],
            field_values={"f_full": "yes"},
            attending=True,
        ),
        SubmitGuestSlotInput(
            id="s2",
            first_name="Beto",
            required_field_ids=["f_full"],
            field_values={"f_full": "yes"},
            attending=True,
        ),
        SubmitGuestSlotInput(
            id="s3",
            first_name="Carla",
            required_field_ids=["f_full"],
            field_values={},
            attending=False,
        ),
        SubmitGuestSlotInput(
            first_name="Diana",
            required_field_ids=["f_full"],
            field_values={"f_full": "gluten free"},
            attending=True,
        ),
        SubmitGuestSlotInput(
            first_name="Edu",
            required_field_ids=["f_full"],
            field_values={},
            attending=False,
        ),
    ]

    product_repo = MagicMock()
    product_repo.get_by_id.return_value = MagicMock(
        additional_info_fields=[MagicMock(field_id="f_full", active=True)],
        max_per_user=5,
    )
    field_repo = MagicMock()
    field_repo.get_by_id.return_value = None

    submit_guest_invitation(
        MagicMock(),
        repo,
        guest_repo,
        product_repo,
        field_repo,
        "inv-1",
        SubmitGuestInvitationInput(guests=guests),
        "2025-01-01T00:00:00Z",
    )

    assert len(guest_repo.last_written) == 5
    assert guest_repo.last_written[0].id == "s1"
    assert guest_repo.last_written[3].first_name == "Diana"
    assert guest_repo.last_written[3].id != "s1"


@patch("application.invitations.submit_guest_invitation.run_update_invitation_with_guest_slots")
def test_submit_rejects_too_many_guest_rows(mock_tx):
    inv = _invitation(guest_slot_count=5)
    repo = _InvitationRepo(inv)
    guest_repo = _GuestSlotRepo([])

    guests = [
        SubmitGuestSlotInput(first_name=f"G{i}", required_field_ids=[], attending=True)
        for i in range(6)
    ]

    with pytest.raises(ValidationError, match="Too many guest rows"):
        submit_guest_invitation(
            MagicMock(),
            repo,
            guest_repo,
            MagicMock(),
            MagicMock(),
            "inv-1",
            SubmitGuestInvitationInput(guests=guests),
            "2025-01-01T00:00:00Z",
        )
    mock_tx.assert_not_called()


@patch("application.invitations.submit_guest_invitation.run_update_invitation_with_guest_slots")
def test_submit_rejects_unknown_slot_id(mock_tx):
    inv = _invitation(guest_slot_count=1)
    repo = _InvitationRepo(inv)
    guest_repo = _GuestSlotRepo([])

    product_repo = MagicMock()
    product_repo.get_by_id.return_value = MagicMock(max_per_user=5)

    with pytest.raises(ValidationError, match="Unknown guest slot id"):
        submit_guest_invitation(
            MagicMock(),
            repo,
            guest_repo,
            product_repo,
            MagicMock(),
            "inv-1",
            SubmitGuestInvitationInput(
                guests=[
                    SubmitGuestSlotInput(
                        id="missing",
                        first_name="Ana",
                        required_field_ids=[],
                        attending=True,
                    )
                ]
            ),
            "2025-01-01T00:00:00Z",
        )
    mock_tx.assert_not_called()


def test_submit_message_only_updates_metadata():
    inv = _invitation()
    repo = _InvitationRepo(inv)
    guest_repo = _GuestSlotRepo([_existing_slot("s1")])

    result = submit_guest_invitation(
        MagicMock(),
        repo,
        guest_repo,
        MagicMock(),
        MagicMock(),
        "inv-1",
        SubmitGuestInvitationInput(message="Hello couple"),
        "2025-01-01T00:00:00Z",
    )

    assert result.metadata[GUEST_MESSAGE_METADATA_KEY] == "Hello couple"
    assert len(guest_repo._slots) == 1


def test_submit_rejects_empty_body():
    inv = _invitation()
    repo = _InvitationRepo(inv)
    guest_repo = _GuestSlotRepo([])

    with pytest.raises(ValidationError, match="At least one of"):
        submit_guest_invitation(
            MagicMock(),
            repo,
            guest_repo,
            MagicMock(),
            MagicMock(),
            "inv-1",
            SubmitGuestInvitationInput(),
            "2025-01-01T00:00:00Z",
        )

import pytest

from application.invitations.validate_invitation_status_transition import (
    validate_invitation_status_transition,
)
from domain.invitations.entity import InvitationStatus
from utils.errors import ValidationError


def test_same_status_allowed() -> None:
    validate_invitation_status_transition(InvitationStatus.CREATED, InvitationStatus.CREATED)


def test_created_to_sent() -> None:
    validate_invitation_status_transition(InvitationStatus.CREATED, InvitationStatus.SENT)


def test_created_to_cancelled() -> None:
    validate_invitation_status_transition(InvitationStatus.CREATED, InvitationStatus.CANCELLED)


def test_sent_to_accepted() -> None:
    validate_invitation_status_transition(InvitationStatus.SENT, InvitationStatus.ACCEPTED)


def test_accepted_to_cancelled() -> None:
    validate_invitation_status_transition(InvitationStatus.ACCEPTED, InvitationStatus.CANCELLED)


def test_created_to_accepted() -> None:
    validate_invitation_status_transition(InvitationStatus.CREATED, InvitationStatus.ACCEPTED)


def test_sent_to_created_rejected() -> None:
    with pytest.raises(ValidationError, match="Invalid invitation status transition"):
        validate_invitation_status_transition(InvitationStatus.SENT, InvitationStatus.CREATED)


def test_declined_to_any_rejected() -> None:
    with pytest.raises(ValidationError, match="Invalid invitation status transition"):
        validate_invitation_status_transition(InvitationStatus.DECLINED, InvitationStatus.SENT)

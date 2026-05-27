from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from api.invitation_access import raise_guest_invitation_access_error
from application.invitations.access_token import (
    access_token_hash_matches,
    generate_access_token,
    hash_access_token,
    invitation_is_expired,
    verify_access_token,
)
from domain.invitations.entity import Invitation, InvitationDestinationType, InvitationStatus


def _invitation(**overrides) -> Invitation:
    raw = generate_access_token()
    base = {
        "id": "inv-1",
        "event_id": "evt-1",
        "inviter_id": "user-1",
        "ticket_id": None,
        "name": "Guest",
        "destination": "guest@example.com",
        "destination_type": InvitationDestinationType.EMAIL,
        "status": InvitationStatus.CREATED,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "guest_slot_count": 0,
        "metadata": {},
        "access_token_hash": hash_access_token(raw),
    }
    base.update(overrides)
    invitation = Invitation(**base)
    return invitation, raw


def test_access_token_hash_matches_rejects_replaced_token():
    invitation, raw = _invitation()
    assert access_token_hash_matches(raw, invitation) is True
    assert access_token_hash_matches(generate_access_token(), invitation) is False


def test_verify_access_token_rejects_expired_invitation():
    invitation, raw = _invitation(
        expires_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
    )
    assert invitation_is_expired(invitation) is True
    assert verify_access_token(raw, invitation) is False


def test_raise_guest_invitation_access_error_prefers_expired_over_invalid_token():
    invitation, _raw = _invitation(
        expires_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
    )
    with pytest.raises(HTTPException) as exc:
        raise_guest_invitation_access_error(invitation, generate_access_token())
    assert exc.value.status_code == 403
    assert exc.value.detail == "invitation_expired"


def test_raise_guest_invitation_access_error_reports_invalid_token():
    invitation, _raw = _invitation()
    with pytest.raises(HTTPException) as exc:
        raise_guest_invitation_access_error(invitation, generate_access_token())
    assert exc.value.status_code == 403
    assert exc.value.detail == "invitation_access_token_invalid"

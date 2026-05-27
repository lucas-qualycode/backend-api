import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

from domain.invitations.entity import Invitation, InvitationStatus

_DEFAULT_PEPPER = "partiiu-invitation-token-dev-pepper-change-in-production"


def _pepper() -> str:
    return os.environ.get("INVITATION_TOKEN_PEPPER", _DEFAULT_PEPPER)


def generate_access_token() -> str:
    return secrets.token_urlsafe(32)


def hash_access_token(raw: str) -> str:
    payload = f"{_pepper()}{raw}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def invitation_is_expired(invitation: Invitation) -> bool:
    expires = _parse_expires_at(invitation.expires_at)
    if expires is None:
        return False
    now = datetime.now(timezone.utc)
    exp = expires if expires.tzinfo else expires.replace(tzinfo=timezone.utc)
    return exp < now


def access_token_hash_matches(raw: str | None, invitation: Invitation) -> bool:
    if not raw or not raw.strip():
        return False
    stored = invitation.access_token_hash
    if not stored:
        return False
    expected = hash_access_token(raw.strip())
    return hmac.compare_digest(expected, stored)


def verify_access_token(raw: str | None, invitation: Invitation) -> bool:
    if not raw or not raw.strip():
        return False
    if invitation.status == InvitationStatus.CANCELLED:
        return False
    if invitation_is_expired(invitation):
        return False
    return access_token_hash_matches(raw, invitation)


def _parse_expires_at(expires_at: str) -> datetime | None:
    raw = (expires_at or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def invitation_json_dict(invitation: Invitation) -> dict:
    data = invitation.model_dump(mode="json")
    data.pop("access_token_hash", None)
    return data

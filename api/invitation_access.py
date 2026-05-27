from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, Request

from api.auth import CurrentUser, _bearer_token
from api.deps import get_event_repository, get_invitation_repository
from application.invitations.access_token import (
    access_token_hash_matches,
    invitation_is_expired,
    verify_access_token,
)
from application.invitations.get_invitation import get_invitation
from domain.events.entity import Event
from domain.events.exceptions import EventNotFoundError
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from firebase_admin import auth as firebase_auth


@dataclass
class InviteAccessContext:
    invitation: Invitation


INVITATION_EXPIRED_DETAIL = "invitation_expired"
INVITATION_ACCESS_TOKEN_INVALID_DETAIL = "invitation_access_token_invalid"


def raise_guest_invitation_access_error(
    invitation: Invitation,
    raw_token: str | None,
) -> None:
    if invitation_is_expired(invitation):
        raise HTTPException(status_code=403, detail=INVITATION_EXPIRED_DETAIL) from None
    if raw_token and not access_token_hash_matches(raw_token, invitation):
        raise HTTPException(
            status_code=403,
            detail=INVITATION_ACCESS_TOKEN_INVALID_DETAIL,
        ) from None
    raise HTTPException(status_code=404, detail="Invitation not found") from None


def get_optional_firebase_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser | None:
    token = _bearer_token(authorization or request.headers.get("authorization"))
    if not token:
        return None
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception:
        return None
    uid = decoded.get("uid")
    if not uid:
        return None
    return CurrentUser(
        uid=uid,
        email=decoded.get("email"),
        role=decoded.get("role", "user"),
    )


def parse_invitation_token(
    x_invitation_token: Annotated[str | None, Header(alias="X-Invitation-Token")] = None,
    token: Annotated[str | None, Query()] = None,
) -> str | None:
    raw = (x_invitation_token or token or "").strip()
    return raw or None


def resolve_invite_access(
    invitation_id: str,
    raw_token: str | None,
    repo,
) -> InviteAccessContext | None:
    if not raw_token:
        return None
    try:
        invitation = get_invitation(repo, invitation_id)
    except InvitationNotFoundError:
        return None
    if not verify_access_token(raw_token, invitation):
        return None
    return InviteAccessContext(invitation=invitation)


def is_event_owner(event: Event, user: CurrentUser | None) -> bool:
    if user is None:
        return False
    return event.created_by == user.uid


def is_invitation_organizer(
    invitation: Invitation,
    event: Event,
    user: CurrentUser | None,
) -> bool:
    if user is None:
        return False
    return user.uid == invitation.inviter_id or user.uid == event.created_by


def can_read_event_as_guest_or_owner(
    event: Event,
    user: CurrentUser | None,
    invite_ctx: InviteAccessContext | None,
    invitation_id_query: str | None,
) -> bool:
    if is_event_owner(event, user):
        return True
    if event.visibility == "public" and invite_ctx is None and invitation_id_query is None:
        return True
    if invite_ctx is not None and invite_ctx.invitation.event_id == event.id:
        if invitation_id_query is None or invitation_id_query == invite_ctx.invitation.id:
            return True
    return False


def require_event_read_access(
    id: str,
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_id: Annotated[str | None, Query()] = None,
    event_repo=Depends(get_event_repository),
    invitation_repo=Depends(get_invitation_repository),
) -> Event:
    try:
        from application.events.get_event import get_event

        event = get_event(event_repo, id)
    except EventNotFoundError:
        raise HTTPException(status_code=404, detail="Event not found") from None

    inv_id = (invitation_id or "").strip() or None
    invitation: Invitation | None = None
    if inv_id:
        try:
            invitation = get_invitation(invitation_repo, inv_id)
        except InvitationNotFoundError:
            invitation = None

    invite_ctx: InviteAccessContext | None = None
    if inv_id and raw_token and invitation is not None:
        if verify_access_token(raw_token, invitation):
            invite_ctx = InviteAccessContext(invitation=invitation)

    if can_read_event_as_guest_or_owner(event, user, invite_ctx, inv_id):
        return event

    if (
        invitation is not None
        and invitation.event_id == event.id
        and user is not None
        and is_invitation_organizer(invitation, event, user)
    ):
        return event

    if (
        inv_id
        and raw_token
        and invitation is not None
        and invitation.event_id == event.id
    ):
        raise_guest_invitation_access_error(invitation, raw_token)

    raise HTTPException(status_code=404, detail="Event not found")


def require_invitation_read_access(
    id: str,
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_repo=Depends(get_invitation_repository),
    event_repo=Depends(get_event_repository),
) -> Invitation:
    try:
        invitation = get_invitation(invitation_repo, id)
    except InvitationNotFoundError:
        raise HTTPException(status_code=404, detail="Invitation not found") from None

    if raw_token and verify_access_token(raw_token, invitation):
        return invitation

    if user is not None:
        try:
            from application.events.get_event import get_event

            event = get_event(event_repo, invitation.event_id)
        except EventNotFoundError:
            raise HTTPException(status_code=404, detail="Invitation not found") from None
        if is_invitation_organizer(invitation, event, user):
            return invitation

    if raw_token:
        raise_guest_invitation_access_error(invitation, raw_token)

    raise HTTPException(status_code=404, detail="Invitation not found")


def require_invitation_token_access(
    id: str,
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_repo=Depends(get_invitation_repository),
) -> InviteAccessContext:
    if not raw_token:
        raise HTTPException(status_code=404, detail="Invitation not found")
    try:
        invitation = get_invitation(invitation_repo, id)
    except InvitationNotFoundError:
        raise HTTPException(status_code=404, detail="Invitation not found") from None
    if verify_access_token(raw_token, invitation):
        return InviteAccessContext(invitation=invitation)
    raise_guest_invitation_access_error(invitation, raw_token)


def require_event_product_list_access(
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    parent_id: Annotated[str | None, Query()] = None,
    event_repo=Depends(get_event_repository),
) -> None:
    scoped_parent = (parent_id or "").strip() or None
    if not scoped_parent:
        return

    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    try:
        from application.events.get_event import get_event

        event = get_event(event_repo, scoped_parent)
    except EventNotFoundError:
        raise HTTPException(status_code=404, detail="Not found") from None

    if not is_event_owner(event, user):
        raise HTTPException(status_code=404, detail="Not found")


def require_guest_catalog_access(
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_id: Annotated[str | None, Query()] = None,
    parent_id: Annotated[str | None, Query()] = None,
    invitation_repo=Depends(get_invitation_repository),
    event_repo=Depends(get_event_repository),
) -> None:
    scoped_parent = (parent_id or "").strip() or None
    inv_id = (invitation_id or "").strip() or None

    if not scoped_parent and not inv_id:
        return

    if scoped_parent and user is not None:
        try:
            from application.events.get_event import get_event

            event = get_event(event_repo, scoped_parent)
            if is_event_owner(event, user):
                return
        except EventNotFoundError:
            pass

    if not inv_id or not raw_token:
        raise HTTPException(status_code=404, detail="Not found")

    try:
        invitation = get_invitation(invitation_repo, inv_id)
    except InvitationNotFoundError:
        raise HTTPException(status_code=404, detail="Not found") from None

    if not verify_access_token(raw_token, invitation):
        raise_guest_invitation_access_error(invitation, raw_token)

    if scoped_parent and invitation.event_id != scoped_parent:
        raise HTTPException(status_code=404, detail="Not found")


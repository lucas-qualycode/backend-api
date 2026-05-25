from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, Request

from api.auth import CurrentUser, _bearer_token
from api.deps import get_event_repository, get_invitation_repository
from application.invitations.access_token import verify_access_token
from application.invitations.get_invitation import get_invitation
from domain.events.entity import Event
from domain.events.exceptions import EventNotFoundError
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from firebase_admin import auth as firebase_auth


@dataclass
class InviteAccessContext:
    invitation: Invitation


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

    invite_ctx: InviteAccessContext | None = None
    inv_id = (invitation_id or "").strip() or None
    if inv_id and raw_token:
        invite_ctx = resolve_invite_access(inv_id, raw_token, invitation_repo)

    if not can_read_event_as_guest_or_owner(event, user, invite_ctx, inv_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return event


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

    raise HTTPException(status_code=404, detail="Invitation not found")


def require_invitation_token_access(
    id: str,
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_repo=Depends(get_invitation_repository),
) -> InviteAccessContext:
    if not raw_token:
        raise HTTPException(status_code=404, detail="Invitation not found")
    ctx = resolve_invite_access(id, raw_token, invitation_repo)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return ctx


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

    ctx = resolve_invite_access(inv_id, raw_token, invitation_repo)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Not found")

    if scoped_parent and ctx.invitation.event_id != scoped_parent:
        raise HTTPException(status_code=404, detail="Not found")


def require_field_definitions_guest_access(
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    raw_token: str | None = Depends(parse_invitation_token),
    invitation_id: Annotated[str | None, Query()] = None,
    invitation_repo=Depends(get_invitation_repository),
    event_repo=Depends(get_event_repository),
) -> None:
    if user is not None and not invitation_id and not raw_token:
        return
    require_guest_catalog_access(
        user=user,
        raw_token=raw_token,
        invitation_id=invitation_id,
        parent_id=None,
        invitation_repo=invitation_repo,
        event_repo=event_repo,
    )

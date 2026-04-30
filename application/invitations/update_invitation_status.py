from application.invitations.validate_invitation_status_transition import (
    validate_invitation_status_transition,
)
from domain.invitations.entity import Invitation, InvitationStatus
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository


def update_invitation_status(
    repo: InvitationRepository,
    invitation_id: str,
    status: InvitationStatus,
    metadata: dict | None,
    *,
    validate_transition: bool = True,
) -> Invitation:
    existing = repo.get_by_id(invitation_id)
    if existing is None:
        raise InvitationNotFoundError(invitation_id)
    if validate_transition:
        validate_invitation_status_transition(existing.status, status)
    result = repo.update_status(invitation_id, status, metadata)
    if result is None:
        raise InvitationNotFoundError(invitation_id)
    return result

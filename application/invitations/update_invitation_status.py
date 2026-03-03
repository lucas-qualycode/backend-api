from backend_api.domain.invitations.entity import Invitation
from backend_api.domain.invitations.exceptions import InvitationNotFoundError
from backend_api.domain.invitations.repository import InvitationRepository


def update_invitation_status(
    repo: InvitationRepository,
    invitation_id: str,
    status: str,
    metadata: dict | None,
) -> Invitation:
    result = repo.update_status(invitation_id, status, metadata)
    if result is None:
        raise InvitationNotFoundError(invitation_id)
    return result

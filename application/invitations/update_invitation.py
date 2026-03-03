from backend_api.application.invitations.schemas import UpdateInvitationInput
from backend_api.domain.invitations.entity import Invitation
from backend_api.domain.invitations.exceptions import InvitationNotFoundError
from backend_api.domain.invitations.repository import InvitationRepository


def update_invitation(
    repo: InvitationRepository,
    invitation_id: str,
    data: UpdateInvitationInput,
    updated_at: str,
) -> Invitation:
    existing = repo.get_by_id(invitation_id)
    if existing is None:
        raise InvitationNotFoundError(invitation_id)
    updates = data.model_dump(exclude_unset=True)
    updated_invitation = existing.model_copy(update={**updates, "updated_at": updated_at})
    return repo.update(invitation_id, updated_invitation)

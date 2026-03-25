from application.invitations.schemas import UpdateInvitationInput
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository


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
    updates.pop("tag_ids", None)
    updated_invitation = existing.model_copy(update={**updates, "updated_at": updated_at})
    return repo.update(invitation_id, updated_invitation)

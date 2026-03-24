from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository


def get_invitation(repo: InvitationRepository, invitation_id: str) -> Invitation:
    invitation = repo.get_by_id(invitation_id)
    if invitation is None:
        raise InvitationNotFoundError(invitation_id)
    return invitation

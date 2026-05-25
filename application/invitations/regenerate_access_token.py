from application.invitations.access_token import generate_access_token, hash_access_token
from application.invitations.get_invitation import get_invitation
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository


def regenerate_invitation_access_token(
    repo: InvitationRepository,
    invitation_id: str,
    now: str,
) -> tuple[Invitation, str]:
    invitation = get_invitation(repo, invitation_id)
    raw = generate_access_token()
    updated = invitation.model_copy(
        update={
            "access_token_hash": hash_access_token(raw),
            "updated_at": now,
        }
    )
    repo.update(invitation_id, updated)
    return updated, raw

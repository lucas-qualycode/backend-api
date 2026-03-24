from domain.invitations.entity import Invitation, InvitationQueryParams
from domain.invitations.repository import InvitationRepository


def list_invitations(
    repo: InvitationRepository,
    query_params: InvitationQueryParams,
) -> list[Invitation]:
    return repo.list(query_params)

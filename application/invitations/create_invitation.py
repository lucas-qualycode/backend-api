import uuid

from backend_api.application.invitations.schemas import CreateInvitationInput
from backend_api.domain.invitations.entity import Invitation
from backend_api.domain.invitations.repository import InvitationRepository


def create_invitation(
    repo: InvitationRepository,
    data: CreateInvitationInput,
    now: str,
) -> Invitation:
    invitation = Invitation(
        id=str(uuid.uuid4()),
        event_id=data.event_id,
        inviter_id=data.inviter_id,
        ticket_ids=data.ticket_ids,
        type=data.type,
        destination=data.destination,
        destination_type=data.destination_type,
        status="PENDING",
        token=str(uuid.uuid4()),
        expires_at=data.expires_at,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
    )
    return repo.create(invitation)

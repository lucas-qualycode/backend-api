from domain.invitation_guest_slots.repository import InvitationGuestSlotRepository
from domain.invitations.repository import InvitationRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def delete_invitation(
    guest_slot_repo: InvitationGuestSlotRepository,
    tagging_repo: TaggingRepository,
    repo: InvitationRepository,
    invitation_id: str,
) -> None:
    guest_slot_repo.delete_all_for_invitation(invitation_id)
    tagging_repo.delete_all_for_entity(TaggingEntityType.INVITATION, invitation_id)
    repo.delete_by_id(invitation_id)

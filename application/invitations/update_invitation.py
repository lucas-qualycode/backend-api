import uuid
from typing import Any

from application.invitations.firestore_update_invitation import run_update_invitation_with_guest_slots
from application.invitations.schemas import CreateInvitationGuestSlotInput, UpdateInvitationInput
from application.invitations.validate_guest_slots import validate_guest_slots_for_create
from application.invitations.validate_invitation_ticket import validate_invitation_ticket_for_event
from domain.invitation_guest_slots.entity import InvitationGuestSlot, InvitationGuestSlotStatus
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository
from domain.products.repository import ProductRepository


def _guest_input_has_content(g: CreateInvitationGuestSlotInput) -> bool:
    return bool(g.first_name) or bool(g.required_field_ids)


def update_invitation(
    db: Any,
    repo: InvitationRepository,
    product_repo: ProductRepository,
    invitation_id: str,
    data: UpdateInvitationInput,
    updated_at: str,
) -> Invitation:
    existing = repo.get_by_id(invitation_id)
    if existing is None:
        raise InvitationNotFoundError(invitation_id)
    raw = data.model_dump(exclude_unset=True)
    slot_refresh = "guest_slot_count" in raw or "guests" in raw
    guests_in: list[CreateInvitationGuestSlotInput]
    if "guests" in raw:
        guests_in = list(data.guests or [])
    else:
        guests_in = []
    patch = {k: v for k, v in raw.items() if k not in ("guests", "tag_ids")}
    next_event_id = patch["event_id"] if "event_id" in patch else existing.event_id
    next_ticket_id = patch["ticket_id"] if "ticket_id" in patch else existing.ticket_id
    if next_ticket_id:
        validate_invitation_ticket_for_event(product_repo, next_ticket_id, next_event_id)
    if slot_refresh:
        total_slots = (
            max(0, int(data.guest_slot_count))
            if data.guest_slot_count is not None
            else existing.guest_slot_count
        )
        patch["guest_slot_count"] = total_slots
        validate_guest_slots_for_create(product_repo, next_ticket_id, total_slots, guests_in)
        filled_guests = [g for g in guests_in if _guest_input_has_content(g)]
        slot_entities: list[InvitationGuestSlot] = []
        for g in filled_guests:
            slot_entities.append(
                InvitationGuestSlot(
                    id=str(uuid.uuid4()),
                    invitation_id=invitation_id,
                    first_name=g.first_name,
                    required_field_ids=list(g.required_field_ids),
                    status=InvitationGuestSlotStatus.PENDING,
                    created_at=updated_at,
                    updated_at=updated_at,
                )
            )
    updated_invitation = existing.model_copy(update={**patch, "updated_at": updated_at})
    if slot_refresh:
        run_update_invitation_with_guest_slots(db, invitation_id, updated_invitation, slot_entities)
        return updated_invitation
    return repo.update(invitation_id, updated_invitation)

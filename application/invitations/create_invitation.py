import uuid
from typing import Any

from application.invitations.firestore_create_invitation import run_create_invitation_with_guest_slots
from application.invitations.schemas import CreateInvitationGuestSlotInput, CreateInvitationInput
from application.invitations.validate_guest_slots import validate_guest_slots_for_create
from application.invitations.validate_invitation_ticket import validate_invitation_ticket_for_event
from domain.invitation_guest_slots.entity import InvitationGuestSlot, InvitationGuestSlotStatus
from domain.invitations.entity import Invitation, InvitationStatus
from domain.field_definitions.repository import FieldDefinitionRepository
from domain.invitations.repository import InvitationRepository
from domain.products.repository import ProductRepository


def _guest_input_has_content(g: CreateInvitationGuestSlotInput) -> bool:
    return bool(g.first_name) or bool(g.required_field_ids)


def create_invitation(
    db: Any,
    repo: InvitationRepository,
    product_repo: ProductRepository,
    field_def_repo: FieldDefinitionRepository,
    data: CreateInvitationInput,
    now: str,
) -> Invitation:
    guests_in = list(data.guests or [])
    total_slots = max(0, int(data.guest_slot_count))
    if data.ticket_id:
        validate_invitation_ticket_for_event(product_repo, data.ticket_id, data.event_id)
    validate_guest_slots_for_create(
        product_repo, field_def_repo, data.ticket_id, total_slots, guests_in
    )
    invitation_id = str(uuid.uuid4())
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
                created_at=now,
                updated_at=now,
            )
        )
    invitation = Invitation(
        id=invitation_id,
        event_id=data.event_id,
        inviter_id=data.inviter_id,
        ticket_id=data.ticket_id,
        name=data.name,
        destination=data.destination,
        destination_type=data.destination_type,
        status=InvitationStatus.CREATED,
        expires_at=data.expires_at,
        created_at=now,
        updated_at=now,
        guest_slot_count=total_slots,
        metadata=data.metadata,
    )
    if slot_entities:
        run_create_invitation_with_guest_slots(db, invitation, slot_entities)
    else:
        repo.create(invitation)
    return invitation

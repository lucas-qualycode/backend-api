import uuid
from datetime import datetime, timezone
from typing import Any

from application.invitations.firestore_update_invitation import run_update_invitation_with_guest_slots
from application.invitations.schemas import SubmitGuestInvitationInput, SubmitGuestSlotInput
from application.invitations.validate_guest_submit import validate_submit_guest_row
from domain.invitation_guest_slots.entity import InvitationGuestSlot, InvitationGuestSlotStatus
from domain.invitation_guest_slots.repository import InvitationGuestSlotRepository
from domain.invitations.entity import Invitation
from domain.invitations.exceptions import InvitationNotFoundError
from domain.invitations.repository import InvitationRepository
from domain.field_definitions.repository import FieldDefinitionRepository
from domain.products.repository import ProductRepository
from utils.errors import ValidationError

GUEST_MESSAGE_METADATA_KEY = "guest_message"


def _parse_expires_at(expires_at: str) -> datetime | None:
    raw = (expires_at or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _ensure_invitation_not_expired(invitation: Invitation) -> None:
    expires = _parse_expires_at(invitation.expires_at)
    if expires is None:
        return
    now = datetime.now(timezone.utc)
    exp = expires if expires.tzinfo else expires.replace(tzinfo=timezone.utc)
    if exp < now:
        raise ValidationError("Invitation has expired")


def _build_slot_entities(
    invitation_id: str,
    guests: list[SubmitGuestSlotInput],
    existing_by_id: dict[str, InvitationGuestSlot],
    now: str,
) -> list[InvitationGuestSlot]:
    seen_ids: set[str] = set()
    built: list[InvitationGuestSlot] = []
    for guest in guests:
        if guest.id:
            if guest.id in seen_ids:
                raise ValidationError(f"Duplicate guest slot id in payload: {guest.id}")
            seen_ids.add(guest.id)
            prior = existing_by_id.get(guest.id)
            if prior is None:
                raise ValidationError(f"Unknown guest slot id: {guest.id}")
            built.append(
                InvitationGuestSlot(
                    id=prior.id,
                    invitation_id=invitation_id,
                    first_name=guest.first_name,
                    required_field_ids=list(guest.required_field_ids),
                    field_values=dict(guest.field_values),
                    attending=guest.attending,
                    status=prior.status,
                    created_at=prior.created_at,
                    updated_at=now,
                )
            )
        else:
            built.append(
                InvitationGuestSlot(
                    id=str(uuid.uuid4()),
                    invitation_id=invitation_id,
                    first_name=guest.first_name,
                    required_field_ids=list(guest.required_field_ids),
                    field_values=dict(guest.field_values),
                    attending=guest.attending,
                    status=InvitationGuestSlotStatus.PENDING,
                    created_at=now,
                    updated_at=now,
                )
            )
    return built


def submit_guest_invitation(
    db: Any,
    repo: InvitationRepository,
    guest_slot_repo: InvitationGuestSlotRepository,
    product_repo: ProductRepository,
    field_def_repo: FieldDefinitionRepository,
    invitation_id: str,
    data: SubmitGuestInvitationInput,
    now: str,
) -> Invitation:
    has_guests = data.guests is not None
    has_message = data.message is not None
    if not has_guests and not has_message:
        raise ValidationError("At least one of guests or message must be provided")

    existing = repo.get_by_id(invitation_id)
    if existing is None:
        raise InvitationNotFoundError(invitation_id)
    _ensure_invitation_not_expired(existing)

    if has_guests:
        guests = list(data.guests or [])
        total_slots = max(0, int(existing.guest_slot_count))
        if len(guests) > total_slots:
            raise ValidationError(
                f"Too many guest rows ({len(guests)}); cannot exceed guest_slot_count ({total_slots})."
            )
        if existing.ticket_id:
            if total_slots < 1:
                raise ValidationError(
                    "guest_slot_count must be at least 1 when a ticket is selected."
                )
            product = product_repo.get_by_id(existing.ticket_id)
            if product is None:
                raise ValidationError("Ticket not found.")
            if total_slots > product.max_per_user:
                raise ValidationError(
                    f"At most {product.max_per_user} guest slot(s) allowed for this ticket (max per user)."
                )
        existing_slots = guest_slot_repo.list_by_invitation_id(invitation_id)
        existing_by_id = {s.id: s for s in existing_slots}
        for i, guest in enumerate(guests):
            validate_submit_guest_row(
                product_repo, field_def_repo, existing.ticket_id, guest, i
            )
        slot_entities = _build_slot_entities(
            invitation_id, guests, existing_by_id, now
        )
        updated_invitation = existing.model_copy(update={"updated_at": now})
        run_update_invitation_with_guest_slots(
            db, invitation_id, updated_invitation, slot_entities
        )
        existing = updated_invitation

    if has_message:
        metadata = dict(existing.metadata or {})
        metadata[GUEST_MESSAGE_METADATA_KEY] = (data.message or "").strip()
        patched = existing.model_copy(update={"metadata": metadata, "updated_at": now})
        updated = repo.update(invitation_id, patched)
        existing = updated if updated is not None else patched

    return existing

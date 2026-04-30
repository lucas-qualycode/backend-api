from application.invitations.schemas import CreateInvitationGuestSlotInput
from domain.products.entity import Product
from domain.products.repository import ProductRepository
from utils.errors import ValidationError


def _allowed_field_ids_for_ticket(product: Product) -> set[str]:
    out: set[str] = set()
    for ref in product.additional_info_fields:
        if ref.active is False:
            continue
        out.add(ref.field_id)
    return out


def validate_guest_slots_for_create(
    product_repo: ProductRepository,
    ticket_id: str | None,
    guest_slot_count: int,
    guests: list[CreateInvitationGuestSlotInput],
) -> None:
    if guest_slot_count < 0:
        raise ValidationError("guest_slot_count must be >= 0")
    if not ticket_id:
        if guest_slot_count > 0:
            raise ValidationError("guest_slot_count requires ticket_id")
        for g in guests:
            if g.required_field_ids:
                raise ValidationError("required_field_ids on guests require ticket_id")
        if len(guests) > guest_slot_count:
            raise ValidationError(
                f"Too many guest detail rows ({len(guests)}); cannot exceed guest_slot_count ({guest_slot_count})."
            )
        return
    if len(guests) > guest_slot_count:
        raise ValidationError(
            f"Too many guest detail rows ({len(guests)}); cannot exceed guest_slot_count ({guest_slot_count})."
        )
    product = product_repo.get_by_id(ticket_id)
    if product is None:
        raise ValidationError("Ticket not found.")
    if guest_slot_count > product.max_per_user:
        raise ValidationError(
            f"At most {product.max_per_user} guest slot(s) allowed for this ticket (max per user)."
        )
    allowed = _allowed_field_ids_for_ticket(product)
    for i, g in enumerate(guests):
        for fid in g.required_field_ids:
            if fid not in allowed:
                raise ValidationError(
                    f"guests[{i}].required_field_ids contains field_id not on this ticket: {fid}"
                )

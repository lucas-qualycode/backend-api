from application.invitations.schemas import SubmitGuestSlotInput
from application.invitations.validate_guest_slots import _allowed_field_ids_for_ticket
from domain.field_definitions.repository import FieldDefinitionRepository
from domain.products.repository import ProductRepository
from utils.errors import ValidationError


def _validate_field_ids_for_ticket(
    product_repo: ProductRepository,
    field_def_repo: FieldDefinitionRepository,
    ticket_id: str | None,
    required_field_ids: list[str],
    row_index: int,
) -> None:
    if not ticket_id:
        if required_field_ids:
            raise ValidationError("required_field_ids on guests require ticket_id")
        return
    product = product_repo.get_by_id(ticket_id)
    if product is None:
        raise ValidationError("Ticket not found.")
    allowed = _allowed_field_ids_for_ticket(product)
    for fid in required_field_ids:
        if fid in allowed:
            continue
        row = field_def_repo.get_by_id(fid)
        if row is None:
            raise ValidationError(
                f"guests[{row_index}].required_field_ids contains unknown field_id: {fid}"
            )
        if row.deleted or not row.active:
            raise ValidationError(
                f"guests[{row_index}].required_field_ids references inactive or deleted field: {fid}"
            )


def _validate_field_values_keys(
    product_repo: ProductRepository,
    field_def_repo: FieldDefinitionRepository,
    ticket_id: str | None,
    field_values: dict[str, str],
    row_index: int,
) -> None:
    if not field_values:
        return
    if not ticket_id:
        raise ValidationError("field_values on guests require ticket_id")
    product = product_repo.get_by_id(ticket_id)
    if product is None:
        raise ValidationError("Ticket not found.")
    allowed = _allowed_field_ids_for_ticket(product)
    for fid in field_values:
        if fid in allowed:
            continue
        row = field_def_repo.get_by_id(fid)
        if row is None:
            raise ValidationError(
                f"guests[{row_index}].field_values contains unknown field_id: {fid}"
            )
        if row.deleted or not row.active:
            raise ValidationError(
                f"guests[{row_index}].field_values references inactive or deleted field: {fid}"
            )


def validate_submit_guest_row(
    product_repo: ProductRepository,
    field_def_repo: FieldDefinitionRepository,
    ticket_id: str | None,
    guest: SubmitGuestSlotInput,
    row_index: int,
) -> None:
    _validate_field_ids_for_ticket(
        product_repo, field_def_repo, ticket_id, list(guest.required_field_ids), row_index
    )
    _validate_field_values_keys(
        product_repo, field_def_repo, ticket_id, dict(guest.field_values), row_index
    )
    if not guest.attending:
        return
    if not guest.first_name.strip():
        raise ValidationError(f"guests[{row_index}].first_name is required when attending")
    for fid in guest.required_field_ids:
        value = (guest.field_values.get(fid) or "").strip()
        if not value:
            raise ValidationError(
                f"guests[{row_index}].field_values missing required value for field_id: {fid}"
            )

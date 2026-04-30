from domain.products.repository import ProductRepository
from domain.products.types import ProductType
from utils.errors import ValidationError


def validate_invitation_ticket_for_event(
    product_repo: ProductRepository,
    ticket_id: str,
    event_id: str,
) -> None:
    product = product_repo.get_by_id(ticket_id)
    if product is None:
        raise ValidationError("Ticket not found.")
    if product.parent_type != "EVENT" or product.parent_id != event_id:
        raise ValidationError("Ticket does not belong to this event.")
    if product.type != ProductType.TICKET:
        raise ValidationError("Product is not a ticket.")

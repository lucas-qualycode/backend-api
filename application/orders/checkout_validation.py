from application.orders.schemas import OrderItemInput
from domain.products.entity import Product
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository
from utils.errors import ValidationError


def _unit_price_cents(product: Product) -> int:
    return 0 if product.is_free else int(product.value)


def validate_and_build_order_items(
    product_repo: ProductRepository,
    items: list[OrderItemInput],
    event_id: str,
) -> tuple[list[OrderItemInput], int]:
    if not items:
        raise ValidationError("At least one line item is required")

    built: list[OrderItemInput] = []
    subtotal = 0

    for raw in items:
        product = product_repo.get_by_id(raw.product_id)
        if product is None:
            raise ProductNotFoundError(raw.product_id)
        if product.deleted:
            raise ValidationError(f"Product is deleted: {raw.product_id}")
        if product.active is False:
            raise ValidationError(f"Product is not active: {raw.product_id}")
        if (product.parent_id or "") != event_id:
            raise ValidationError(f"Product does not belong to this event: {raw.product_id}")

        quantity = raw.quantity if raw.quantity > 0 else 1
        expected_unit = _unit_price_cents(product)
        expected_total = expected_unit * quantity

        if raw.unit_price is not None and raw.unit_price != expected_unit:
            raise ValidationError(f"Invalid unit price for product {raw.product_id}")
        if raw.total_price is not None and raw.total_price != expected_total:
            raise ValidationError(f"Invalid total price for product {raw.product_id}")

        item_meta = dict(raw.metadata)
        if raw.name:
            item_meta.setdefault("display_name", raw.name)

        built.append(
            OrderItemInput(
                product_id=raw.product_id,
                product_type=raw.product_type or product.type,
                quantity=quantity,
                unit_price=expected_unit,
                total_price=expected_total,
                currency=raw.currency or "BRL",
                metadata=item_meta,
            )
        )
        subtotal += expected_total

    return built, subtotal


def assert_total_cents_matches(subtotal: int, total_cents: int | None) -> None:
    if total_cents is not None and total_cents != subtotal:
        raise ValidationError("total_cents does not match server-calculated total")

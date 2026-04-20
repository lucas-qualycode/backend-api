import uuid

from application.orders.schemas import CreateOrderInput
from application.orders.validate_additional_data import validate_order_items_additional_data
from domain.field_definitions.repository import FieldDefinitionRepository
from domain.orders.entity import Order, OrderItem
from domain.orders.repository import OrderRepository
from domain.products.repository import ProductRepository


def create_order(
    order_repo: OrderRepository,
    product_repo: ProductRepository,
    field_repo: FieldDefinitionRepository,
    data: CreateOrderInput,
    now: str,
) -> Order:
    validate_order_items_additional_data(product_repo, field_repo, data.items)
    items = []
    subtotal = 0
    for it in data.items:
        total_price = it.total_price if it.total_price is not None else it.quantity * it.unit_price
        subtotal += total_price
        legacy_additional = it.metadata.get("additional_data") if isinstance(it.metadata, dict) else None
        additional_data = (
            it.additional_data
            if it.additional_data is not None
            else legacy_additional if isinstance(legacy_additional, list) else []
        )
        items.append(
            OrderItem(
                id=str(uuid.uuid4()),
                product_id=it.product_id,
                product_type=it.product_type,
                quantity=it.quantity,
                unit_price=it.unit_price,
                total_price=total_price,
                currency=it.currency,
                metadata=it.metadata,
                additional_data=additional_data,
            )
        )
    tax_amount = 0
    discount_amount = 0
    total_amount = subtotal + tax_amount - discount_amount
    expires_at = data.expires_at or now
    order = Order(
        id=str(uuid.uuid4()),
        user_id=data.user_id,
        parent_id=data.parent_id,
        invitation_id=data.invitation_id,
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        currency=data.currency,
        status="CREATED",
        payment_provider="mercadopago",
        created_at=now,
        updated_at=now,
        expires_at=expires_at,
        metadata=data.metadata,
    )
    return order_repo.create(order)

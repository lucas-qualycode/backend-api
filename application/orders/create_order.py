import uuid

from backend_api.application.orders.schemas import CreateOrderInput
from backend_api.domain.orders.entity import Order, OrderItem
from backend_api.domain.orders.repository import OrderRepository


def create_order(
    repo: OrderRepository,
    data: CreateOrderInput,
    now: str,
) -> Order:
    items = []
    subtotal = 0
    for it in data.items:
        total_price = it.total_price if it.total_price is not None else it.quantity * it.unit_price
        subtotal += total_price
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
    return repo.create(order)

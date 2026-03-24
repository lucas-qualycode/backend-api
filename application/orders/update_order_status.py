from domain.orders.entity import Order
from domain.orders.exceptions import OrderNotFoundError
from domain.orders.repository import OrderRepository


def update_order_status(
    repo: OrderRepository,
    order_id: str,
    status: str,
) -> Order:
    result = repo.update_status(order_id, status)
    if result is None:
        raise OrderNotFoundError(order_id)
    return result

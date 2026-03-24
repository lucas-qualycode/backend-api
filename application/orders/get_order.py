from domain.orders.entity import Order
from domain.orders.exceptions import OrderNotFoundError
from domain.orders.repository import OrderRepository


def get_order(repo: OrderRepository, order_id: str) -> Order:
    order = repo.get_by_id(order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return order

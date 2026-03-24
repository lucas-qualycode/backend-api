from domain.orders.entity import Order, OrderQueryParams
from domain.orders.repository import OrderRepository


def list_orders(
    repo: OrderRepository,
    query_params: OrderQueryParams,
) -> list[Order]:
    return repo.list(query_params)

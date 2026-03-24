from abc import ABC, abstractmethod

from domain.orders.entity import Order, OrderQueryParams


class OrderRepository(ABC):
    @abstractmethod
    def create(self, order: Order) -> Order:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Order | None:
        ...

    @abstractmethod
    def list(self, query_params: OrderQueryParams) -> list[Order]:
        ...

    @abstractmethod
    def update(self, id: str, order: Order) -> Order:
        ...

    @abstractmethod
    def update_status(self, id: str, status: str) -> Order | None:
        ...

from abc import ABC, abstractmethod

from domain.payments.entity import Payment, PaymentQueryParams


class PaymentRepository(ABC):
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Payment | None:
        ...

    @abstractmethod
    def list(self, query_params: PaymentQueryParams) -> list[Payment]:
        ...

    @abstractmethod
    def update(self, id: str, payment: Payment) -> Payment:
        ...

    @abstractmethod
    def update_status(self, id: str, status: str) -> Payment | None:
        ...

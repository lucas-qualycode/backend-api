from abc import ABC, abstractmethod

from domain.user_products.entity import UserProduct, UserProductQueryParams


class UserProductRepository(ABC):
    @abstractmethod
    def create(self, user_product: UserProduct) -> UserProduct:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> UserProduct | None:
        ...

    @abstractmethod
    def list(self, query_params: UserProductQueryParams) -> list[UserProduct]:
        ...

    @abstractmethod
    def update(self, id: str, user_product: UserProduct) -> UserProduct:
        ...

    @abstractmethod
    def update_status(self, id: str, status: str) -> UserProduct | None:
        ...

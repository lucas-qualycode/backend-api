from abc import ABC, abstractmethod

from domain.products.entity import Product, ProductQueryParams


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Product | None:
        ...

    @abstractmethod
    def list(self, query_params: ProductQueryParams) -> list[Product]:
        ...

    @abstractmethod
    def update(self, id: str, product: Product) -> Product:
        ...

    @abstractmethod
    def soft_delete(self, id: str) -> None:
        ...

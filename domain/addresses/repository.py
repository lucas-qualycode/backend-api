from abc import ABC, abstractmethod

from backend_api.domain.addresses.entity import Address, AddressQueryParams


class AddressRepository(ABC):
    @abstractmethod
    def create(self, address: Address) -> Address:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Address | None:
        ...

    @abstractmethod
    def list(self, query_params: AddressQueryParams) -> list[Address]:
        ...

    @abstractmethod
    def update(self, id: str, address: Address) -> Address:
        ...

    @abstractmethod
    def delete(self, id: str) -> None:
        ...

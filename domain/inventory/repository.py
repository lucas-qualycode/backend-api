from abc import ABC, abstractmethod

from domain.inventory.entity import InventoryItem, InventoryQueryParams


class InventoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> InventoryItem | None:
        ...

    @abstractmethod
    def create(self, item: InventoryItem) -> InventoryItem:
        ...

    @abstractmethod
    def update(self, id: str, updates: dict) -> InventoryItem | None:
        ...

    @abstractmethod
    def reserve(self, id: str, quantity: int) -> bool:
        ...

    @abstractmethod
    def release(self, id: str, quantity: int) -> bool:
        ...

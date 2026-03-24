from abc import ABC, abstractmethod

from domain.event_types.entity import EventType, EventTypeQueryParams


class EventTypeRepository(ABC):
    @abstractmethod
    def create(self, event_type: EventType) -> EventType:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> EventType | None:
        ...

    @abstractmethod
    def list(self, query_params: EventTypeQueryParams) -> list[EventType]:
        ...

    @abstractmethod
    def update(self, id: str, event_type: EventType) -> EventType:
        ...

    @abstractmethod
    def soft_delete(self, id: str, last_updated_by: str) -> EventType | None:
        ...

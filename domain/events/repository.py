from abc import ABC, abstractmethod

from domain.events.entity import Event, EventQueryParams


class EventRepository(ABC):
    @abstractmethod
    def create(self, event: Event) -> Event:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Event | None:
        ...

    @abstractmethod
    def list(self, query_params: EventQueryParams) -> list[Event]:
        ...

    @abstractmethod
    def update(self, id: str, event: Event) -> Event:
        ...

    @abstractmethod
    def soft_delete(self, id: str, last_updated_by: str) -> Event | None:
        ...

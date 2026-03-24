from abc import ABC, abstractmethod

from domain.stands.entity import Stand, StandQueryParams


class StandRepository(ABC):
    @abstractmethod
    def create(self, stand: Stand, event_id: str) -> Stand:
        ...

    @abstractmethod
    def get_by_id(self, id: str, event_id: str) -> Stand | None:
        ...

    @abstractmethod
    def list(self, event_id: str, query_params: StandQueryParams) -> list[Stand]:
        ...

    @abstractmethod
    def update(self, id: str, event_id: str, stand: Stand) -> Stand:
        ...

    @abstractmethod
    def soft_delete(self, id: str, event_id: str, last_updated_by: str) -> Stand | None:
        ...

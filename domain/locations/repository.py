from abc import ABC, abstractmethod

from domain.locations.entity import Location, LocationQueryParams


class LocationRepository(ABC):
    @abstractmethod
    def create(self, location: Location) -> Location:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Location | None:
        ...

    @abstractmethod
    def get_by_ids(self, ids: list[str]) -> dict[str, Location]:
        ...

    @abstractmethod
    def list(self, query_params: LocationQueryParams) -> list[Location]:
        ...

    @abstractmethod
    def update(self, id: str, location: Location) -> Location:
        ...

    @abstractmethod
    def soft_delete(self, id: str, last_updated_by: str) -> Location | None:
        ...

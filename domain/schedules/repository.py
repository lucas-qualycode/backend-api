from abc import ABC, abstractmethod

from domain.schedules.entity import Schedule, ScheduleQueryParams


class ScheduleRepository(ABC):
    @abstractmethod
    def create(self, schedule: Schedule) -> Schedule:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Schedule | None:
        ...

    @abstractmethod
    def list(self, query_params: ScheduleQueryParams) -> list[Schedule]:
        ...

    @abstractmethod
    def update(self, id: str, schedule: Schedule) -> Schedule:
        ...

    @abstractmethod
    def delete(self, id: str) -> None:
        ...

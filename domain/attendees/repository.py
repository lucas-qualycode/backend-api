from abc import ABC, abstractmethod

from backend_api.domain.attendees.entity import Attendee, AttendeeQueryParams


class AttendeeRepository(ABC):
    @abstractmethod
    def create(self, attendee: Attendee, event_id: str) -> Attendee:
        ...

    @abstractmethod
    def get_by_id(self, id: str, event_id: str) -> Attendee | None:
        ...

    @abstractmethod
    def list(self, event_id: str, query_params: AttendeeQueryParams) -> list[Attendee]:
        ...

    @abstractmethod
    def update_status(self, id: str, event_id: str, status: str, check_in_time: str | None) -> Attendee | None:
        ...

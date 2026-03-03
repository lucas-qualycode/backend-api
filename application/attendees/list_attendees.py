from backend_api.domain.attendees.entity import Attendee, AttendeeQueryParams
from backend_api.domain.attendees.repository import AttendeeRepository


def list_attendees(
    repo: AttendeeRepository,
    event_id: str,
    query_params: AttendeeQueryParams,
) -> list[Attendee]:
    return repo.list(event_id, query_params)

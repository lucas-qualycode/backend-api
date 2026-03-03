from backend_api.domain.attendees.entity import Attendee
from backend_api.domain.attendees.exceptions import AttendeeNotFoundError
from backend_api.domain.attendees.repository import AttendeeRepository


def update_attendee_status(
    repo: AttendeeRepository,
    attendee_id: str,
    event_id: str,
    status: str,
    check_in_time: str | None,
) -> Attendee:
    result = repo.update_status(attendee_id, event_id, status, check_in_time)
    if result is None:
        raise AttendeeNotFoundError(attendee_id)
    return result

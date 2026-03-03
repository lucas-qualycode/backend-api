from backend_api.domain.attendees.entity import Attendee
from backend_api.domain.attendees.exceptions import AttendeeNotFoundError
from backend_api.domain.attendees.repository import AttendeeRepository


def get_attendee(
    repo: AttendeeRepository,
    attendee_id: str,
    event_id: str,
) -> Attendee:
    attendee = repo.get_by_id(attendee_id, event_id)
    if attendee is None:
        raise AttendeeNotFoundError(attendee_id)
    return attendee

import uuid

from backend_api.application.attendees.schemas import CreateAttendeeInput
from backend_api.domain.attendees.entity import Attendee
from backend_api.domain.attendees.repository import AttendeeRepository


def create_attendee(
    repo: AttendeeRepository,
    data: CreateAttendeeInput,
    event_id: str,
    now: str,
) -> Attendee:
    attendee = Attendee(
        id=str(uuid.uuid4()),
        event_id=event_id,
        user_id=data.user_id,
        user_product_id=data.user_product_id,
        invitation_id=data.invitation_id,
        status="REGISTERED",
        check_in_time=None,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
    )
    return repo.create(attendee, event_id)

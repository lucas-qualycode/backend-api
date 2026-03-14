import uuid

from backend_api.domain.attendees.entity import Attendee, AttendeeQueryParams, AttendeeStatus
from backend_api.domain.attendees.repository import AttendeeRepository
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.domain.events.repository import EventRepository
from backend_api.domain.user_products.repository import UserProductRepository


class UserProductNotFoundError(Exception):
    pass


class UserProductNotForEventError(Exception):
    pass


def check_in_attendee(
    event_repo: EventRepository,
    user_product_repo: UserProductRepository,
    attendee_repo: AttendeeRepository,
    event_id: str,
    user_product_id: str,
    now: str,
) -> Attendee:
    event = event_repo.get_by_id(event_id)
    if event is None:
        raise EventNotFoundError(event_id)
    user_product = user_product_repo.get_by_id(user_product_id)
    if user_product is None:
        raise UserProductNotFoundError()
    if user_product.parent_id != event_id:
        raise UserProductNotForEventError()
    qp = AttendeeQueryParams(event_id=event_id, user_product_id=user_product_id)
    existing_list = attendee_repo.list(event_id, qp)
    existing = existing_list[0] if existing_list else None
    if existing:
        if existing.status == AttendeeStatus.CHECKED_IN:
            return existing
        updated = attendee_repo.update_status(
            existing.id, event_id, AttendeeStatus.CHECKED_IN, now
        )
        return updated
    new_attendee = Attendee(
        id=str(uuid.uuid4()),
        event_id=event_id,
        user_id=user_product.user_id,
        user_product_id=user_product_id,
        invitation_id=user_product.invitation_id,
        status=AttendeeStatus.CHECKED_IN,
        check_in_time=now,
        created_at=now,
        updated_at=now,
        metadata={},
    )
    return attendee_repo.create(new_attendee, event_id)

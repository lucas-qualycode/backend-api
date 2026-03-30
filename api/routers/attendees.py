from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import CurrentUser, UserOrGuestListAuth, get_current_user, get_user_or_guest_list
from api.deps import get_attendee_repository, get_event_repository, get_user_product_repository
from application.attendees import (
    check_in_attendee,
    create_attendee,
    get_attendee,
    list_attendees,
    update_attendee_status,
)
from application.attendees.check_in_attendee import UserProductNotForEventError, UserProductNotFoundError
from application.attendees.schemas import CreateAttendeeInput, CreateAttendeeRequest
from domain.attendees.entity import AttendeeQueryParams
from domain.attendees.exceptions import AttendeeNotFoundError
from domain.events.exceptions import EventNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/events", tags=["attendees"])


class CheckInBody(BaseModel):
    user_product_id: str


class UpdateAttendeeStatusBody(BaseModel):
    status: str
    check_in_time: str | None = None


@router.get("/{event_id}/attendees")
def list_attendees_endpoint(
    event_id: str,
    auth: UserOrGuestListAuth = Depends(get_user_or_guest_list),
    user_id: str | None = None,
    user_product_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_attendee_repository),
):
    uid = user_id or (auth.user.uid if auth.user else None)
    params = AttendeeQueryParams(
        event_id=event_id,
        user_id=uid,
        user_product_id=user_product_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    items = list_attendees(repo, event_id, params)
    return [a.model_dump(mode="json") for a in items]


@router.get("/{event_id}/attendees/{id}")
def get_attendee_endpoint(
    event_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_attendee_repository),
):
    try:
        return get_attendee(repo, id, event_id).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{event_id}/attendees", status_code=201)
def create_attendee_endpoint(
    event_id: str,
    data: CreateAttendeeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_attendee_repository),
):
    try:
        data_with_user = CreateAttendeeInput(**data.model_dump(), user_id=current_user.uid)
        return create_attendee(repo, data_with_user, event_id, get_timestamp()).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{event_id}/attendees/check-in")
def check_in_attendee_endpoint(
    event_id: str,
    body: CheckInBody,
    auth: UserOrGuestListAuth = Depends(get_user_or_guest_list),
    event_repo=Depends(get_event_repository),
    user_product_repo=Depends(get_user_product_repository),
    attendee_repo=Depends(get_attendee_repository),
):
    if auth.user and auth.user.role not in ("admin", "organizer"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    try:
        attendee = check_in_attendee(
            event_repo,
            user_product_repo,
            attendee_repo,
            event_id,
            body.user_product_id,
            get_timestamp(),
        )
        return attendee.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserProductNotFoundError:
        raise HTTPException(status_code=404, detail="User product not found")
    except UserProductNotForEventError:
        raise HTTPException(status_code=400, detail="User product does not belong to this event")


@router.patch("/{event_id}/attendees/{id}/status")
def update_attendee_status_endpoint(
    event_id: str,
    id: str,
    body: UpdateAttendeeStatusBody,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_attendee_repository),
):
    try:
        return update_attendee_status(repo, id, event_id, body.status, body.check_in_time).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

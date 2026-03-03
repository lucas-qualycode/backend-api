from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend_api.api.deps import get_attendee_repository
from backend_api.application.attendees import (
    create_attendee,
    get_attendee,
    list_attendees,
    update_attendee_status,
)
from backend_api.application.attendees.schemas import CreateAttendeeInput
from backend_api.domain.attendees.entity import AttendeeQueryParams
from backend_api.domain.attendees.exceptions import AttendeeNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/events", tags=["attendees"])


class UpdateAttendeeStatusBody(BaseModel):
    status: str
    check_in_time: str | None = None


@router.get("/{event_id}/attendees")
def list_attendees_endpoint(
    event_id: str,
    user_id: str | None = None,
    user_product_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_attendee_repository),
):
    params = AttendeeQueryParams(
        event_id=event_id,
        user_id=user_id,
        user_product_id=user_product_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    items = list_attendees(repo, event_id, params)
    return [a.model_dump(mode="json") for a in items]


@router.get("/{event_id}/attendees/{id}")
def get_attendee_endpoint(event_id: str, id: str, repo=Depends(get_attendee_repository)):
    try:
        return get_attendee(repo, id, event_id).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{event_id}/attendees", status_code=201)
def create_attendee_endpoint(
    event_id: str,
    data: CreateAttendeeInput,
    repo=Depends(get_attendee_repository),
):
    try:
        return create_attendee(repo, data, event_id, get_timestamp()).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{event_id}/attendees/{id}/status")
def update_attendee_status_endpoint(
    event_id: str,
    id: str,
    body: UpdateAttendeeStatusBody,
    repo=Depends(get_attendee_repository),
):
    try:
        return update_attendee_status(repo, id, event_id, body.status, body.check_in_time).model_dump(mode="json")
    except AttendeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

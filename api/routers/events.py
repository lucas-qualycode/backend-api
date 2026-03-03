from fastapi import APIRouter, Depends, Header, HTTPException

from backend_api.api.deps import get_event_repository
from backend_api.application.events import (
    create_event,
    delete_event,
    get_event,
    list_events,
    update_event,
)
from backend_api.application.events.schemas import CreateEventInput, UpdateEventInput
from backend_api.domain.events.entity import EventQueryParams
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events_endpoint(
    name: str | None = None,
    active: bool | None = None,
    is_paid: bool | None = None,
    is_online: bool | None = None,
    deleted: bool | None = None,
    type_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_event_repository),
):
    params = EventQueryParams(
        name=name,
        active=active,
        is_paid=is_paid,
        is_online=is_online,
        deleted=deleted,
        type_id=type_id,
        limit=limit,
        offset=offset,
    )
    events = list_events(repo, params)
    return [e.model_dump(mode="json") for e in events]


@router.get("/{id}")
def get_event_endpoint(id: str, repo=Depends(get_event_repository)):
    try:
        event = get_event(repo, id)
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_event_endpoint(
    data: CreateEventInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_event_repository),
):
    event = create_event(repo, data, x_user_id, get_timestamp())
    return event.model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_event_endpoint(
    id: str,
    data: UpdateEventInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_event_repository),
):
    try:
        event = update_event(repo, id, data, x_user_id, get_timestamp())
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}")
def delete_event_endpoint(
    id: str,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_event_repository),
):
    try:
        event = delete_event(repo, id, x_user_id)
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

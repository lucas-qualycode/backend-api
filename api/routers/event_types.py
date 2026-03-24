from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer, get_current_user
from api.deps import get_event_type_repository
from application.event_types import (
    create_event_type,
    delete_event_type,
    get_event_type,
    list_event_types,
    update_event_type,
)
from application.event_types.schemas import CreateEventTypeInput, UpdateEventTypeInput
from domain.event_types.entity import EventTypeQueryParams
from domain.event_types.exceptions import EventTypeNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/event-types", tags=["event-types"])


@router.get("")
def list_event_types_endpoint(
    name: str | None = None,
    active: bool | None = None,
    deleted: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_event_type_repository),
):
    params = EventTypeQueryParams(name=name, active=active, deleted=deleted, limit=limit, offset=offset)
    items = list_event_types(repo, params)
    return [e.model_dump(mode="json") for e in items]


@router.get("/{id}")
def get_event_type_endpoint(id: str, repo=Depends(get_event_type_repository)):
    try:
        return get_event_type(repo, id).model_dump(mode="json")
    except EventTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_event_type_endpoint(
    data: CreateEventTypeInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_type_repository),
):
    return create_event_type(repo, data, current_user.uid, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_event_type_endpoint(
    id: str,
    data: UpdateEventTypeInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_type_repository),
):
    try:
        return update_event_type(repo, id, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except EventTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}")
def delete_event_type_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_type_repository),
):
    try:
        return delete_event_type(repo, id, current_user.uid).model_dump(mode="json")
    except EventTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

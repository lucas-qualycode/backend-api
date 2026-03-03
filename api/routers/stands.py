from fastapi import APIRouter, Depends, Header, HTTPException

from backend_api.api.deps import get_stand_repository
from backend_api.application.stands import (
    create_stand,
    delete_stand,
    get_stand,
    list_stands,
    update_stand,
)
from backend_api.application.stands.schemas import CreateStandInput, UpdateStandInput
from backend_api.domain.stands.entity import StandQueryParams
from backend_api.domain.stands.exceptions import StandNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/events", tags=["stands"])


@router.get("/{event_id}/stands")
def list_stands_endpoint(
    event_id: str,
    name: str | None = None,
    status: str | None = None,
    zone: str | None = None,
    deleted: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_stand_repository),
):
    params = StandQueryParams(name=name, status=status, zone=zone, deleted=deleted, limit=limit, offset=offset)
    items = list_stands(repo, event_id, params)
    return [s.model_dump(mode="json") for s in items]


@router.get("/{event_id}/stands/{id}")
def get_stand_endpoint(event_id: str, id: str, repo=Depends(get_stand_repository)):
    try:
        return get_stand(repo, id, event_id).model_dump(mode="json")
    except StandNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{event_id}/stands", status_code=201)
def create_stand_endpoint(
    event_id: str,
    data: CreateStandInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_stand_repository),
):
    try:
        return create_stand(repo, data, event_id, x_user_id, get_timestamp()).model_dump(mode="json")
    except StandNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{event_id}/stands/{id}")
@router.patch("/{event_id}/stands/{id}")
def update_stand_endpoint(
    event_id: str,
    id: str,
    data: UpdateStandInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_stand_repository),
):
    try:
        return update_stand(repo, id, event_id, data, x_user_id, get_timestamp()).model_dump(mode="json")
    except StandNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{event_id}/stands/{id}")
def delete_stand_endpoint(
    event_id: str,
    id: str,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_stand_repository),
):
    try:
        return delete_stand(repo, id, event_id, x_user_id).model_dump(mode="json")
    except StandNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

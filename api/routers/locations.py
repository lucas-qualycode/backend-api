from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import CurrentUser, RequireOrganizer
from api.deps import get_location_repository
from application.locations import (
    create_location,
    delete_location,
    get_location,
    list_locations,
    update_location,
)
from application.locations.schemas import CreateLocationInput, UpdateLocationInput
from domain.locations.entity import LocationQueryParams
from domain.locations.exceptions import LocationNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("")
def list_locations_endpoint(
    deleted: bool | None = Query(default=None),
    limit: int | None = None,
    offset: int | None = None,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_location_repository),
):
    params = LocationQueryParams(
        created_by=current_user.uid,
        deleted=deleted if deleted is not None else False,
        limit=limit,
        offset=offset,
    )
    items = list_locations(repo, params)
    return [loc.model_dump(mode="json") for loc in items]


@router.get("/{id}")
def get_location_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_location_repository),
):
    try:
        loc = get_location(repo, id)
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if loc.created_by != current_user.uid:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc.model_dump(mode="json")


@router.post("", status_code=201)
def create_location_endpoint(
    data: CreateLocationInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_location_repository),
):
    try:
        return create_location(repo, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{id}")
@router.patch("/{id}")
def update_location_endpoint(
    id: str,
    data: UpdateLocationInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_location_repository),
):
    try:
        return update_location(repo, id, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{id}")
def delete_location_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_location_repository),
):
    try:
        return delete_location(repo, id, current_user.uid).model_dump(mode="json")
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

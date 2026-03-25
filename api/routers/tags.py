from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import CurrentUser, RequireOrganizer
from api.deps import get_tag_repository
from application.tags import create_tag, delete_tag, get_tag, list_tags, update_tag
from application.tags.schemas import CreateTagInput, UpdateTagInput
from domain.tags.entity import TagQueryParams
from domain.tags.exceptions import TagNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def list_tags_endpoint(
    name: str | None = None,
    active: bool | None = None,
    deleted: bool | None = None,
    parent_tag_id: str | None = None,
    applies_to: str | None = None,
    roots_only: bool = Query(default=False),
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_tag_repository),
):
    if roots_only and parent_tag_id is not None:
        raise HTTPException(status_code=400, detail="Cannot use roots_only with parent_tag_id")
    params = TagQueryParams(
        name=name,
        active=active,
        deleted=deleted,
        parent_tag_id=parent_tag_id,
        applies_to=applies_to,
        roots_only=roots_only,
        limit=limit,
        offset=offset,
    )
    items = list_tags(repo, params)
    return [t.model_dump(mode="json") for t in items]


@router.get("/{id}")
def get_tag_endpoint(id: str, repo=Depends(get_tag_repository)):
    try:
        return get_tag(repo, id).model_dump(mode="json")
    except TagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_tag_endpoint(
    data: CreateTagInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_tag_repository),
):
    try:
        return create_tag(repo, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{id}")
@router.patch("/{id}")
def update_tag_endpoint(
    id: str,
    data: UpdateTagInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_tag_repository),
):
    try:
        return update_tag(repo, id, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except TagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{id}")
def delete_tag_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_tag_repository),
):
    try:
        return delete_tag(repo, id, current_user.uid).model_dump(mode="json")
    except TagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

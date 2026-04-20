from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer
from api.deps import get_field_definition_repository
from application.field_definitions import (
    create_field_definition,
    get_field_definition,
    list_field_definitions,
    update_field_definition,
)
from application.field_definitions.schemas import (
    CreateFieldDefinitionInput,
    UpdateFieldDefinitionInput,
)
from domain.field_definitions.entity import FieldDefinitionQueryParams
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/field-definitions", tags=["field-definitions"])


@router.get("")
def list_field_definitions_endpoint(
    active: bool | None = None,
    deleted: bool | None = None,
    field_type: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_field_definition_repository),
):
    params = FieldDefinitionQueryParams(
        active=active,
        deleted=deleted,
        field_type=field_type,
        limit=limit,
        offset=offset,
    )
    items = list_field_definitions(repo, params)
    return [x.model_dump(mode="json") for x in items]


@router.get("/{id}")
def get_field_definition_endpoint(id: str, repo=Depends(get_field_definition_repository)):
    try:
        return get_field_definition(repo, id).model_dump(mode="json")
    except FieldDefinitionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_field_definition_endpoint(
    data: CreateFieldDefinitionInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_field_definition_repository),
):
    try:
        return create_field_definition(
            repo, data, current_user.uid, get_timestamp()
        ).model_dump(mode="json")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{id}")
@router.patch("/{id}")
def update_field_definition_endpoint(
    id: str,
    data: UpdateFieldDefinitionInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_field_definition_repository),
):
    try:
        return update_field_definition(
            repo, id, data, current_user.uid, get_timestamp()
        ).model_dump(mode="json")
    except FieldDefinitionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

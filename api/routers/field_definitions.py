from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer
from api.deps import get_field_definition_repository
from api.field_definitions_public import (
    assert_public_readable,
    rate_limit_field_definitions_read,
    resolve_list_query_params,
    serialize_field_definition,
)
from api.invitation_access import get_optional_firebase_user
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
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    _rate_limit: None = Depends(rate_limit_field_definitions_read),
    repo=Depends(get_field_definition_repository),
):
    params, public_response = resolve_list_query_params(
        user,
        active=active,
        deleted=deleted,
        field_type=field_type,
        limit=limit,
        offset=offset,
    )
    items = list_field_definitions(repo, params)
    return [serialize_field_definition(x, public=public_response) for x in items]


@router.get("/{id}")
def get_field_definition_endpoint(
    id: str,
    user: CurrentUser | None = Depends(get_optional_firebase_user),
    _rate_limit: None = Depends(rate_limit_field_definitions_read),
    repo=Depends(get_field_definition_repository),
):
    try:
        row = get_field_definition(repo, id)
    except FieldDefinitionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None

    public_response = user is None
    if public_response:
        assert_public_readable(row)

    return serialize_field_definition(row, public=public_response)


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

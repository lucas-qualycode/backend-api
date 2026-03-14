from fastapi import APIRouter, Depends, HTTPException, Query

from backend_api.api.auth import CurrentUser, get_current_user
from backend_api.api.deps import get_address_repository
from backend_api.application.addresses import (
    create_address,
    delete_address,
    get_address,
    list_addresses,
    update_address,
)
from backend_api.application.addresses.schemas import CreateAddressInput, UpdateAddressInput
from backend_api.domain.addresses.entity import AddressQueryParams
from backend_api.domain.addresses.exceptions import AddressNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("")
def list_addresses_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    user_id: str | None = None,
    type_: str | None = Query(None, alias="type"),
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_address_repository),
):
    params = AddressQueryParams(user_id=user_id or current_user.uid, type=type_, limit=limit, offset=offset)
    items = list_addresses(repo, params)
    return [a.model_dump(mode="json") for a in items]


@router.get("/{id}")
def get_address_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_address_repository),
):
    try:
        return get_address(repo, id).model_dump(mode="json")
    except AddressNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_address_endpoint(
    data: CreateAddressInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_address_repository),
):
    data_with_user = data.model_copy(update={"userId": current_user.uid})
    return create_address(repo, data_with_user, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_address_endpoint(
    id: str,
    data: UpdateAddressInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_address_repository),
):
    try:
        return update_address(repo, id, data, get_timestamp()).model_dump(mode="json")
    except AddressNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
def delete_address_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_address_repository),
):
    try:
        delete_address(repo, id)
    except AddressNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

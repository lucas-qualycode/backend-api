from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import CurrentUser, get_current_user
from api.deps import get_user_product_repository
from application.user_products import (
    create_user_product,
    get_user_product,
    list_user_products,
    update_user_product,
    update_user_product_status,
)
from application.user_products.schemas import CreateUserProductInput, UpdateUserProductInput
from domain.user_products.entity import UserProductQueryParams
from domain.user_products.exceptions import UserProductNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/user-products", tags=["user-products"])


class UpdateUserProductStatusBody(BaseModel):
    status: str


@router.get("")
def list_user_products_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    parent_id: str | None = None,
    user_id: str | None = None,
    product_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_user_product_repository),
):
    params = UserProductQueryParams(
        parent_id=parent_id,
        user_id=user_id or current_user.uid,
        product_id=product_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    items = list_user_products(repo, params)
    return [u.model_dump(mode="json") for u in items]


@router.get("/{id}")
def get_user_product_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_product_repository),
):
    try:
        return get_user_product(repo, id).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_user_product_endpoint(
    data: CreateUserProductInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_product_repository),
):
    data_with_user = data.model_copy(update={"user_id": current_user.uid})
    return create_user_product(repo, data_with_user, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_user_product_endpoint(
    id: str,
    data: UpdateUserProductInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_product_repository),
):
    try:
        return update_user_product(repo, id, data, get_timestamp()).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{id}/status")
def update_user_product_status_endpoint(
    id: str,
    body: UpdateUserProductStatusBody,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_product_repository),
):
    try:
        return update_user_product_status(repo, id, body.status).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

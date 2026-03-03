from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend_api.api.deps import get_user_product_repository
from backend_api.application.user_products import (
    create_user_product,
    get_user_product,
    list_user_products,
    update_user_product,
    update_user_product_status,
)
from backend_api.application.user_products.schemas import CreateUserProductInput, UpdateUserProductInput
from backend_api.domain.user_products.entity import UserProductQueryParams
from backend_api.domain.user_products.exceptions import UserProductNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/user-products", tags=["user-products"])


class UpdateUserProductStatusBody(BaseModel):
    status: str


@router.get("")
def list_user_products_endpoint(
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
        user_id=user_id,
        product_id=product_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    items = list_user_products(repo, params)
    return [u.model_dump(mode="json") for u in items]


@router.get("/{id}")
def get_user_product_endpoint(id: str, repo=Depends(get_user_product_repository)):
    try:
        return get_user_product(repo, id).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_user_product_endpoint(data: CreateUserProductInput, repo=Depends(get_user_product_repository)):
    return create_user_product(repo, data, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_user_product_endpoint(id: str, data: UpdateUserProductInput, repo=Depends(get_user_product_repository)):
    try:
        return update_user_product(repo, id, data, get_timestamp()).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{id}/status")
def update_user_product_status_endpoint(
    id: str,
    body: UpdateUserProductStatusBody,
    repo=Depends(get_user_product_repository),
):
    try:
        return update_user_product_status(repo, id, body.status).model_dump(mode="json")
    except UserProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

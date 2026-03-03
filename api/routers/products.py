from fastapi import APIRouter, Depends, Header, HTTPException

from backend_api.api.deps import get_product_repository
from backend_api.application.products import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)
from backend_api.application.products.schemas import CreateProductInput, UpdateProductInput
from backend_api.domain.products.entity import ProductQueryParams
from backend_api.domain.products.exceptions import ProductNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products_endpoint(
    name: str | None = None,
    parent_id: str | None = None,
    active: bool | None = None,
    deleted: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_product_repository),
):
    params = ProductQueryParams(name=name, parent_id=parent_id, active=active, deleted=deleted, limit=limit, offset=offset)
    items = list_products(repo, params)
    return [p.model_dump(mode="json") for p in items]


@router.get("/{id}")
def get_product_endpoint(id: str, repo=Depends(get_product_repository)):
    try:
        return get_product(repo, id).model_dump(mode="json")
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_product_endpoint(
    data: CreateProductInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_product_repository),
):
    return create_product(repo, data, x_user_id, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_product_endpoint(
    id: str,
    data: UpdateProductInput,
    x_user_id: str = Header("", alias="X-User-Id"),
    repo=Depends(get_product_repository),
):
    try:
        return update_product(repo, id, data, x_user_id, get_timestamp()).model_dump(mode="json")
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
def delete_product_endpoint(id: str, repo=Depends(get_product_repository)):
    try:
        delete_product(repo, id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

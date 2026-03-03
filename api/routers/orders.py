from fastapi import APIRouter, Depends, HTTPException

from backend_api.api.deps import get_order_repository
from backend_api.application.orders import create_order, get_order, list_orders, update_order_status
from backend_api.application.orders.schemas import CreateOrderInput, UpdateOrderStatusInput
from backend_api.domain.orders.entity import OrderQueryParams
from backend_api.domain.orders.exceptions import OrderNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders_endpoint(
    user_id: str | None = None,
    parent_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_order_repository),
):
    params = OrderQueryParams(user_id=user_id, parent_id=parent_id, status=status, limit=limit, offset=offset)
    items = list_orders(repo, params)
    return [o.model_dump(mode="json") for o in items]


@router.get("/{id}")
def get_order_endpoint(id: str, repo=Depends(get_order_repository)):
    try:
        return get_order(repo, id).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_order_endpoint(data: CreateOrderInput, repo=Depends(get_order_repository)):
    return create_order(repo, data, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
def update_order_endpoint(id: str, data: UpdateOrderStatusInput, repo=Depends(get_order_repository)):
    try:
        return update_order_status(repo, id, data.status).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{id}/status")
def update_order_status_endpoint(id: str, data: UpdateOrderStatusInput, repo=Depends(get_order_repository)):
    try:
        return update_order_status(repo, id, data.status).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

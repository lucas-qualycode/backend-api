from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, get_current_user
from api.deps import get_order_repository
from application.orders import create_order, get_order, list_orders, update_order_status
from application.orders.schemas import CreateOrderInput, UpdateOrderStatusInput
from domain.orders.entity import OrderQueryParams
from domain.orders.exceptions import OrderNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    user_id: str | None = None,
    parent_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_order_repository),
):
    params = OrderQueryParams(user_id=user_id or current_user.uid, parent_id=parent_id, status=status, limit=limit, offset=offset)
    items = list_orders(repo, params)
    return [o.model_dump(mode="json") for o in items]


@router.get("/{id}")
def get_order_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_order_repository),
):
    try:
        return get_order(repo, id).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_order_endpoint(
    data: CreateOrderInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_order_repository),
):
    data_with_user = data.model_copy(update={"user_id": current_user.uid})
    return create_order(repo, data_with_user, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
def update_order_endpoint(
    id: str,
    data: UpdateOrderStatusInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_order_repository),
):
    try:
        return update_order_status(repo, id, data.status).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{id}/status")
def update_order_status_endpoint(
    id: str,
    data: UpdateOrderStatusInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_order_repository),
):
    try:
        return update_order_status(repo, id, data.status).model_dump(mode="json")
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

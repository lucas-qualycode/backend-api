from fastapi import APIRouter, Depends, HTTPException

from backend_api.api.auth import CurrentUser, get_current_user
from backend_api.api.deps import get_payment_repository
from backend_api.application.payments import (
    create_payment,
    get_payment,
    list_payments,
    update_payment_status,
)
from backend_api.application.payments.schemas import CreatePaymentInput, UpdatePaymentStatusInput
from backend_api.domain.payments.entity import PaymentQueryParams
from backend_api.domain.payments.exceptions import PaymentNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("")
def list_payments_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    user_id: str | None = None,
    order_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_payment_repository),
):
    params = PaymentQueryParams(user_id=user_id or current_user.uid, order_id=order_id, status=status, limit=limit, offset=offset)
    items = list_payments(repo, params)
    return [p.model_dump(mode="json") for p in items]


@router.get("/{id}")
def get_payment_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_payment_repository),
):
    try:
        return get_payment(repo, id).model_dump(mode="json")
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_payment_endpoint(
    data: CreatePaymentInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_payment_repository),
):
    data_with_user = data.model_copy(update={"user_id": current_user.uid})
    return create_payment(repo, data_with_user, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_payment_endpoint(
    id: str,
    data: UpdatePaymentStatusInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_payment_repository),
):
    try:
        return update_payment_status(repo, id, data.status).model_dump(mode="json")
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{id}/status")
def update_payment_status_endpoint(
    id: str,
    data: UpdatePaymentStatusInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_payment_repository),
):
    try:
        return update_payment_status(repo, id, data.status).model_dump(mode="json")
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

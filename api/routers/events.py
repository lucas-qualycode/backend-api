from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer, UserOrGuestListAuth, get_current_user, get_user_or_guest_list
from api.deps import get_event_repository, get_user_product_repository
from application.events import (
    create_event,
    delete_event,
    generate_guest_list_token,
    get_event,
    list_events,
    update_event,
)
from application.events.schemas import CreateEventInput, UpdateEventInput
from application.user_products.list_user_products import list_user_products
from domain.events.entity import EventQueryParams
from domain.events.exceptions import EventNotFoundError
from domain.user_products.entity import UserProductQueryParams
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events_endpoint(
    name: str | None = None,
    active: bool | None = None,
    is_paid: bool | None = None,
    is_online: bool | None = None,
    deleted: bool | None = None,
    type_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_event_repository),
):
    params = EventQueryParams(
        name=name,
        active=active,
        is_paid=is_paid,
        is_online=is_online,
        deleted=deleted,
        type_id=type_id,
        limit=limit,
        offset=offset,
    )
    events = list_events(repo, params)
    return [e.model_dump(mode="json") for e in events]


@router.get("/{id}")
def get_event_endpoint(id: str, repo=Depends(get_event_repository)):
    try:
        event = get_event(repo, id)
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{id}/user-products")
def list_event_user_products_endpoint(
    id: str,
    auth: UserOrGuestListAuth = Depends(get_user_or_guest_list),
    event_repo=Depends(get_event_repository),
    user_product_repo=Depends(get_user_product_repository),
):
    try:
        get_event(event_repo, id)
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    params = UserProductQueryParams(parent_id=id, status="ACTIVE")
    items = list_user_products(user_product_repo, params)
    return [u.model_dump(mode="json") for u in items]


@router.post("/{id}/guest-list-token")
def generate_guest_list_token_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
):
    try:
        token = generate_guest_list_token(repo, id, current_user.uid, get_timestamp())
        return {"token": token}
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_event_endpoint(
    data: CreateEventInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
):
    event = create_event(repo, data, current_user.uid, get_timestamp())
    return event.model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_event_endpoint(
    id: str,
    data: UpdateEventInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
):
    try:
        event = update_event(repo, id, data, current_user.uid, get_timestamp())
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}")
def delete_event_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
):
    try:
        event = delete_event(repo, id, current_user.uid)
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

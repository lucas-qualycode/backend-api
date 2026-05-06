from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer, UserOrGuestListAuth, get_user_or_guest_list
from api.deps import (
    get_event_repository,
    get_location_repository,
    get_tag_repository,
    get_tagging_repository,
    get_user_product_repository,
)
from application.events import (
    create_event,
    delete_event,
    generate_guest_list_token,
    get_event,
    list_events_as_dicts,
    update_event,
)
from application.events.embed_event_response import embed_event_response_dict
from application.events.schemas import CreateEventInput, UpdateEventInput
from application.taggings import validate_tag_ids_for_entity
from application.user_products.list_user_products import list_user_products
from domain.events.entity import EventQueryParams
from domain.events.exceptions import EventNotFoundError
from domain.taggings.entity import TaggingEntityType
from domain.user_products.entity import UserProductQueryParams
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events_endpoint(
    name: str | None = None,
    active: bool | None = None,
    is_paid: bool | None = None,
    is_online: bool | None = None,
    deleted: bool | None = None,
    created_by: str | None = None,
    tag_id: str | None = None,
    primary_category: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    event_repo=Depends(get_event_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    location_repo=Depends(get_location_repository),
):
    params = EventQueryParams(
        name=name,
        active=active,
        is_paid=is_paid,
        is_online=is_online,
        deleted=deleted,
        created_by=created_by,
        tag_id=tag_id,
        primary_category=primary_category,
        limit=limit,
        offset=offset,
    )
    return list_events_as_dicts(event_repo, tagging_repo, tag_repo, location_repo, params)


@router.get("/{id}")
def get_event_endpoint(
    id: str,
    event_repo=Depends(get_event_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    location_repo=Depends(get_location_repository),
):
    try:
        event = get_event(event_repo, id)
        return embed_event_response_dict(event, tagging_repo, tag_repo, location_repo)
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
    location_repo=Depends(get_location_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        validate_tag_ids_for_entity(
            tag_repo,
            data.tag_ids,
            TaggingEntityType.EVENT,
            require_at_least_one=True,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    now = get_timestamp()
    try:
        event = create_event(repo, location_repo, data, current_user.uid, now)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    tagging_repo.replace_all_for_entity(
        TaggingEntityType.EVENT,
        event.id,
        data.tag_ids,
        current_user.uid,
        now,
    )
    return embed_event_response_dict(event, tagging_repo, tag_repo, location_repo)


@router.put("/{id}")
@router.patch("/{id}")
def update_event_endpoint(
    id: str,
    data: UpdateEventInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
    location_repo=Depends(get_location_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        now = get_timestamp()
        try:
            event = update_event(repo, location_repo, id, data, current_user.uid, now)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)
        if data.tag_ids is not None:
            try:
                validate_tag_ids_for_entity(
                    tag_repo,
                    data.tag_ids,
                    TaggingEntityType.EVENT,
                    require_at_least_one=True,
                )
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=e.message)
            tagging_repo.replace_all_for_entity(
                TaggingEntityType.EVENT,
                event.id,
                data.tag_ids,
                current_user.uid,
                now,
            )
        return embed_event_response_dict(event, tagging_repo, tag_repo, location_repo)
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}")
def delete_event_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_event_repository),
    tagging_repo=Depends(get_tagging_repository),
):
    try:
        event = delete_event(repo, tagging_repo, id, current_user.uid)
        return event.model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

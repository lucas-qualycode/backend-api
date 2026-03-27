from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer
from api.deps import get_event_repository, get_schedule_repository
from application.schedules import (
    create_schedule,
    delete_schedule,
    get_schedule,
    list_schedules,
    update_schedule,
)
from application.schedules.event_access import ensure_user_owns_event
from application.schedules.schemas import CreateScheduleInput, UpdateScheduleInput
from domain.events.exceptions import EventNotFoundError
from domain.schedules.entity import ScheduleQueryParams
from domain.schedules.exceptions import ScheduleNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("")
def list_schedules_endpoint(
    event_id: str,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        ensure_user_owns_event(event_repo, event_id, current_user.uid)
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    params = ScheduleQueryParams(event_id=event_id, status=status, limit=limit, offset=offset)
    items = list_schedules(repo, params)
    return [s.model_dump(mode="json") for s in items]


@router.get("/{id}")
def get_schedule_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        schedule = get_schedule(repo, id)
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    try:
        ensure_user_owns_event(event_repo, schedule.event_id, current_user.uid)
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return schedule.model_dump(mode="json")


@router.post("", status_code=201)
def create_schedule_endpoint(
    data: CreateScheduleInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        return create_schedule(
            repo, event_repo, data, current_user.uid, get_timestamp()
        ).model_dump(mode="json")
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{id}")
@router.patch("/{id}")
def update_schedule_endpoint(
    id: str,
    data: UpdateScheduleInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        return update_schedule(
            repo, event_repo, id, data, current_user.uid, get_timestamp()
        ).model_dump(mode="json")
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{id}", status_code=204)
def delete_schedule_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        delete_schedule(repo, event_repo, id, current_user.uid)
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

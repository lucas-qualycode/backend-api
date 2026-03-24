from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer, get_current_user
from api.deps import get_schedule_repository
from application.schedules import (
    create_schedule,
    delete_schedule,
    get_schedule,
    list_schedules,
    update_schedule,
)
from application.schedules.schemas import CreateScheduleInput, UpdateScheduleInput
from domain.schedules.entity import ScheduleQueryParams
from domain.schedules.exceptions import ScheduleNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("")
def list_schedules_endpoint(
    event_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_schedule_repository),
):
    params = ScheduleQueryParams(event_id=event_id, status=status, limit=limit, offset=offset)
    items = list_schedules(repo, params)
    return [s.model_dump(mode="json") for s in items]


@router.get("/{id}")
def get_schedule_endpoint(id: str, repo=Depends(get_schedule_repository)):
    try:
        return get_schedule(repo, id).model_dump(mode="json")
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_schedule_endpoint(
    data: CreateScheduleInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
):
    return create_schedule(repo, data, current_user.uid, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_schedule_endpoint(
    id: str,
    data: UpdateScheduleInput,
    current_user: CurrentUser = RequireOrganizer,
    repo=Depends(get_schedule_repository),
):
    try:
        return update_schedule(repo, id, data, current_user.uid, get_timestamp()).model_dump(mode="json")
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
def delete_schedule_endpoint(id: str, repo=Depends(get_schedule_repository)):
    try:
        delete_schedule(repo, id)
    except ScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

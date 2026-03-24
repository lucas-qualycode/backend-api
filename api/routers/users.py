from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, get_current_user
from api.deps import get_user_repository
from application.users import create_user, get_user, update_user
from application.users.schemas import CreateUserInput, UpdateUserInput
from domain.users.exceptions import UserNotFoundError
from infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
def create_user_endpoint(
    data: CreateUserInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_repository),
):
    data_with_id = data.model_copy(update={"id": current_user.uid})
    return create_user(repo, data_with_id, get_timestamp()).model_dump(mode="json")


@router.get("/{id}")
def get_user_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_repository),
):
    if id != current_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return get_user(repo, id).model_dump(mode="json")
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id}")
@router.patch("/{id}")
def update_user_endpoint(
    id: str,
    data: UpdateUserInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_user_repository),
):
    if id != current_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return update_user(repo, id, data, get_timestamp()).model_dump(mode="json")
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

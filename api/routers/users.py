from fastapi import APIRouter, Depends, HTTPException

from backend_api.api.deps import get_user_repository
from backend_api.application.users import create_user, get_user, update_user
from backend_api.application.users.schemas import CreateUserInput, UpdateUserInput
from backend_api.domain.users.exceptions import UserNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
def create_user_endpoint(data: CreateUserInput, repo=Depends(get_user_repository)):
    return create_user(repo, data, get_timestamp()).model_dump(mode="json")


@router.get("/{id}")
def get_user_endpoint(id: str, repo=Depends(get_user_repository)):
    try:
        return get_user(repo, id).model_dump(mode="json")
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id}")
@router.patch("/{id}")
def update_user_endpoint(id: str, data: UpdateUserInput, repo=Depends(get_user_repository)):
    try:
        return update_user(repo, id, data, get_timestamp()).model_dump(mode="json")
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

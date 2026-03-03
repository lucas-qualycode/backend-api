from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend_api.api.deps import get_invitation_repository
from backend_api.application.invitations import (
    create_invitation,
    get_invitation,
    list_invitations,
    update_invitation,
    update_invitation_status,
)
from backend_api.application.invitations.schemas import CreateInvitationInput, UpdateInvitationInput
from backend_api.domain.invitations.entity import InvitationQueryParams
from backend_api.domain.invitations.exceptions import InvitationNotFoundError
from backend_api.infrastructure.persistence.firestore_common import get_timestamp

router = APIRouter(prefix="/invitations", tags=["invitations"])


class UpdateInvitationStatusBody(BaseModel):
    status: str
    metadata: dict[str, Any] | None = None


@router.get("")
def list_invitations_endpoint(
    event_id: str | None = None,
    inviter_id: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_invitation_repository),
):
    params = InvitationQueryParams(event_id=event_id, inviter_id=inviter_id, status=status, limit=limit, offset=offset)
    items = list_invitations(repo, params)
    return [i.model_dump(mode="json") for i in items]


@router.get("/{id}")
def get_invitation_endpoint(id: str, repo=Depends(get_invitation_repository)):
    try:
        return get_invitation(repo, id).model_dump(mode="json")
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_invitation_endpoint(data: CreateInvitationInput, repo=Depends(get_invitation_repository)):
    return create_invitation(repo, data, get_timestamp()).model_dump(mode="json")


@router.put("/{id}")
@router.patch("/{id}")
def update_invitation_endpoint(id: str, data: UpdateInvitationInput, repo=Depends(get_invitation_repository)):
    try:
        return update_invitation(repo, id, data, get_timestamp()).model_dump(mode="json")
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{id}/status")
def update_invitation_status_endpoint(
    id: str,
    body: UpdateInvitationStatusBody,
    repo=Depends(get_invitation_repository),
):
    try:
        return update_invitation_status(repo, id, body.status, body.metadata).model_dump(mode="json")
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

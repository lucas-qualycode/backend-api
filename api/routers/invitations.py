from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import CurrentUser, get_current_user, get_optional_user
from api.deps import get_invitation_repository, get_tag_repository, get_tagging_repository
from application.invitations import (
    create_invitation,
    get_invitation,
    list_invitations_as_dicts,
    update_invitation,
    update_invitation_status,
)
from application.invitations.schemas import CreateInvitationInput, UpdateInvitationInput
from application.taggings import embed_tags_on_invitation, validate_tag_ids_for_entity
from domain.invitations.entity import InvitationQueryParams
from domain.invitations.exceptions import InvitationNotFoundError
from domain.taggings.entity import TaggingEntityType
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/invitations", tags=["invitations"])


class UpdateInvitationStatusBody(BaseModel):
    status: str
    metadata: dict[str, Any] | None = None


@router.get("")
def list_invitations_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    event_id: str | None = None,
    inviter_id: str | None = None,
    status: str | None = None,
    tag_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_invitation_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    params = InvitationQueryParams(
        event_id=event_id,
        inviter_id=inviter_id or current_user.uid,
        status=status,
        limit=limit,
        offset=offset,
        tag_id=tag_id,
    )
    return list_invitations_as_dicts(repo, tagging_repo, tag_repo, params)


@router.get("/{id}")
def get_invitation_endpoint(
    id: str,
    current_user: CurrentUser | None = Depends(get_optional_user),
    repo=Depends(get_invitation_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        invitation = get_invitation(repo, id)
        return embed_tags_on_invitation(invitation, tagging_repo, tag_repo)
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_invitation_endpoint(
    data: CreateInvitationInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invitation_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        validate_tag_ids_for_entity(
            tag_repo,
            data.tag_ids,
            TaggingEntityType.INVITATION,
            require_at_least_one=False,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    now = get_timestamp()
    invitation = create_invitation(repo, data, now)
    tagging_repo.replace_all_for_entity(
        TaggingEntityType.INVITATION,
        invitation.id,
        data.tag_ids,
        current_user.uid,
        now,
    )
    return embed_tags_on_invitation(invitation, tagging_repo, tag_repo)


@router.put("/{id}")
@router.patch("/{id}")
def update_invitation_endpoint(
    id: str,
    data: UpdateInvitationInput,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invitation_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        now = get_timestamp()
        invitation = update_invitation(repo, id, data, now)
        if data.tag_ids is not None:
            try:
                validate_tag_ids_for_entity(
                    tag_repo,
                    data.tag_ids,
                    TaggingEntityType.INVITATION,
                    require_at_least_one=False,
                )
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=e.message)
            tagging_repo.replace_all_for_entity(
                TaggingEntityType.INVITATION,
                invitation.id,
                data.tag_ids,
                current_user.uid,
                now,
            )
        return embed_tags_on_invitation(invitation, tagging_repo, tag_repo)
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{id}/status")
def update_invitation_status_endpoint(
    id: str,
    body: UpdateInvitationStatusBody,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invitation_repository),
):
    try:
        return update_invitation_status(repo, id, body.status, body.metadata).model_dump(mode="json")
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

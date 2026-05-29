from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from pydantic import BaseModel

from api.auth import CurrentUser, get_current_user
from api.invitation_access import (
    is_invitation_organizer,
    require_invitation_read_access,
    require_invitation_token_access,
)
from api.deps import (
    get_checkout_intent_repository,
    get_db,
    get_event_repository,
    get_field_definition_repository,
    get_inventory_repository,
    get_invitation_guest_slot_repository,
    get_invitation_repository,
    get_order_repository,
    get_payment_repository,
    get_product_repository,
    get_tag_repository,
    get_tagging_repository,
)
from application.invitations.confirmation import get_invitation_confirmation
from application.invitations.guest_payment import get_active_checkout, get_guest_payment_status
from application.invitations import (
    create_invitation,
    delete_invitation,
    get_invitation,
    list_invitations_as_dicts,
    submit_guest_invitation,
    update_invitation,
    update_invitation_status,
)
from application.invitations.schemas import (
    CreateInvitationInput,
    SubmitGuestInvitationInput,
    UpdateInvitationInput,
)
from application.orders.schemas import InvitationCheckoutRequest
from application.products import list_products_as_dicts
from domain.products.exceptions import ProductNotFoundError
from application.invitations.checkout import process_invitation_checkout
from infrastructure.mercadopago.client import MercadoPagoApiError
from application.taggings import embed_tags_on_invitation, validate_tag_ids_for_entity
from domain.invitations.entity import InvitationQueryParams, InvitationStatus
from domain.invitations.exceptions import InvitationNotFoundError
from domain.payments.exceptions import PaymentNotFoundError
from domain.products.entity import ProductQueryParams
from domain.products.types import ProductType
from domain.taggings.entity import TaggingEntityType
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/invitations", tags=["invitations"])


class UpdateInvitationStatusBody(BaseModel):
    status: InvitationStatus
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
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
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
    return list_invitations_as_dicts(
        repo, tagging_repo, tag_repo, guest_slot_repo, params
    )


@router.get("/{id}")
def get_invitation_endpoint(
    id: str,
    invitation=Depends(require_invitation_read_access),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    out = embed_tags_on_invitation(invitation, tagging_repo, tag_repo)
    out.pop("access_token_hash", None)
    slots = guest_slot_repo.list_by_invitation_id(id)
    out["guest_slots"] = [s.model_dump(mode="json") for s in slots]
    return out


@router.get("/{id}/products")
def list_invitation_products_endpoint(
    id: str,
    invitation=Depends(require_invitation_read_access),
    name: str | None = None,
    type: ProductType | None = None,
    active: bool | None = None,
    deleted: bool | None = None,
    tag_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    product_repo=Depends(get_product_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    inventory_repo=Depends(get_inventory_repository),
):
    params = ProductQueryParams(
        name=name,
        parent_id=invitation.event_id,
        type=type,
        active=active,
        deleted=deleted,
        limit=limit,
        offset=offset,
        tag_id=tag_id,
    )
    return list_products_as_dicts(
        product_repo, tagging_repo, tag_repo, inventory_repo, params
    )


@router.get("/{id}/checkout/active")
def get_active_checkout_endpoint(
    id: str,
    invitation=Depends(require_invitation_read_access),
    order_repo=Depends(get_order_repository),
    payment_repo=Depends(get_payment_repository),
):
    try:
        return get_active_checkout(
            invitation.id,
            order_repo=order_repo,
            payment_repo=payment_repo,
        ).model_dump(mode="json")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.get("/{id}/payments/{payment_id}")
def get_guest_payment_status_endpoint(
    id: str,
    payment_id: str,
    invitation=Depends(require_invitation_read_access),
    order_repo=Depends(get_order_repository),
    payment_repo=Depends(get_payment_repository),
):
    try:
        return get_guest_payment_status(
            invitation.id,
            payment_id,
            order_repo=order_repo,
            payment_repo=payment_repo,
        ).model_dump(mode="json")
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.get("/{id}/confirmation")
def get_invitation_confirmation_endpoint(
    id: str,
    invitation=Depends(require_invitation_read_access),
    order_repo=Depends(get_order_repository),
    payment_repo=Depends(get_payment_repository),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
):
    return get_invitation_confirmation(
        invitation,
        order_repo=order_repo,
        payment_repo=payment_repo,
        guest_slot_repo=guest_slot_repo,
    ).model_dump(mode="json")


@router.post("/{id}/checkout")
def invitation_checkout_endpoint(
    id: str,
    data: InvitationCheckoutRequest,
    invitation=Depends(require_invitation_read_access),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    order_repo=Depends(get_order_repository),
    payment_repo=Depends(get_payment_repository),
    product_repo=Depends(get_product_repository),
    checkout_intent_repo=Depends(get_checkout_intent_repository),
):
    key = (idempotency_key or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    try:
        result = process_invitation_checkout(
            invitation,
            data,
            idempotency_key=key,
            order_repo=order_repo,
            payment_repo=payment_repo,
            product_repo=product_repo,
            checkout_intent_repo=checkout_intent_repo,
            now=get_timestamp(),
        )
        return result.model_dump(mode="json")
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e
    except MercadoPagoApiError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/{id}/guest-submit")
def submit_guest_invitation_endpoint(
    id: str,
    data: SubmitGuestInvitationInput,
    _access: object = Depends(require_invitation_token_access),
    db=Depends(get_db),
    repo=Depends(get_invitation_repository),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
    product_repo=Depends(get_product_repository),
    field_def_repo=Depends(get_field_definition_repository),
):
    try:
        now = get_timestamp()
        invitation = submit_guest_invitation(
            db,
            repo,
            guest_slot_repo,
            product_repo,
            field_def_repo,
            id,
            data,
            now,
        )
        out = invitation.model_dump(mode="json")
        out.pop("access_token_hash", None)
        slots = guest_slot_repo.list_by_invitation_id(id)
        out["guest_slots"] = [s.model_dump(mode="json") for s in slots]
        return out
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/{id}/access-token")
def regenerate_invitation_access_token_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invitation_repository),
    event_repo=Depends(get_event_repository),
):
    try:
        invitation = get_invitation(repo, id)
        from application.events.get_event import get_event

        event = get_event(event_repo, invitation.event_id)
        if not is_invitation_organizer(invitation, event, current_user):
            raise HTTPException(status_code=403, detail="Forbidden")
        from application.invitations.regenerate_access_token import (
            regenerate_invitation_access_token,
        )

        now = get_timestamp()
        _updated, raw = regenerate_invitation_access_token(repo, id, now)
        return {"access_token": raw}
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("", status_code=201)
def create_invitation_endpoint(
    data: CreateInvitationInput,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    repo=Depends(get_invitation_repository),
    product_repo=Depends(get_product_repository),
    field_def_repo=Depends(get_field_definition_repository),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
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
    invitation, raw_access_token = create_invitation(
        db, repo, product_repo, field_def_repo, data, now
    )
    tagging_repo.replace_all_for_entity(
        TaggingEntityType.INVITATION,
        invitation.id,
        data.tag_ids,
        current_user.uid,
        now,
    )
    out = embed_tags_on_invitation(invitation, tagging_repo, tag_repo)
    out.pop("access_token_hash", None)
    if invitation.guest_slot_count:
        slots = guest_slot_repo.list_by_invitation_id(invitation.id)
        out["guest_slots"] = [s.model_dump(mode="json") for s in slots]
    out["access_token"] = raw_access_token
    return out


@router.put("/{id}")
@router.patch("/{id}")
def update_invitation_endpoint(
    id: str,
    data: UpdateInvitationInput,
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
    repo=Depends(get_invitation_repository),
    product_repo=Depends(get_product_repository),
    field_def_repo=Depends(get_field_definition_repository),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
):
    try:
        prior = get_invitation(repo, id)
        if prior.inviter_id != current_user.uid:
            raise HTTPException(status_code=403, detail="Forbidden")
        now = get_timestamp()
        invitation = update_invitation(
            db, repo, product_repo, field_def_repo, id, data, now
        )
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
        out = embed_tags_on_invitation(invitation, tagging_repo, tag_repo)
        out.pop("access_token_hash", None)
        slots = guest_slot_repo.list_by_invitation_id(invitation.id)
        if slots:
            out["guest_slots"] = [s.model_dump(mode="json") for s in slots]
        return out
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
def delete_invitation_endpoint(
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invitation_repository),
    guest_slot_repo=Depends(get_invitation_guest_slot_repository),
    tagging_repo=Depends(get_tagging_repository),
):
    try:
        prior = get_invitation(repo, id)
        if prior.inviter_id != current_user.uid:
            raise HTTPException(status_code=403, detail="Forbidden")
        delete_invitation(guest_slot_repo, tagging_repo, repo, id)
        return Response(status_code=204)
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

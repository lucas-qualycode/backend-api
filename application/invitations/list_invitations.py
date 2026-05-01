from application.taggings.embed import embed_tags_on_invitations
from domain.invitation_guest_slots.repository import InvitationGuestSlotRepository
from domain.invitations.entity import Invitation, InvitationQueryParams
from domain.invitations.repository import InvitationRepository
from domain.tags.repository import TagRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def _params_without_tag_filter(q: InvitationQueryParams) -> InvitationQueryParams:
    return InvitationQueryParams(
        event_id=q.event_id,
        inviter_id=q.inviter_id,
        status=q.status,
        limit=q.limit,
        offset=q.offset,
    )


def list_invitations(
    repo: InvitationRepository,
    query_params: InvitationQueryParams,
) -> list[Invitation]:
    return repo.list(_params_without_tag_filter(query_params))


def _attach_guest_slots(rows: list[dict], guest_slot_repo: InvitationGuestSlotRepository) -> None:
    for d in rows:
        n = d.get("guest_slot_count") or 0
        if n > 0:
            slots = guest_slot_repo.list_by_invitation_id(str(d["id"]))
            d["guest_slots"] = [s.model_dump(mode="json") for s in slots]
        else:
            d["guest_slots"] = []


def list_invitations_as_dicts(
    invitation_repo: InvitationRepository,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
    guest_slot_repo: InvitationGuestSlotRepository,
    query_params: InvitationQueryParams,
) -> list[dict]:
    if query_params.tag_id:
        rows = tagging_repo.list_by_tag(
            TaggingEntityType.INVITATION,
            query_params.tag_id,
            query_params.limit,
            query_params.offset,
        )
        invitations: list[Invitation] = []
        for r in rows:
            inv = invitation_repo.get_by_id(r.entity_id)
            if inv is None:
                continue
            if query_params.event_id is not None and inv.event_id != query_params.event_id:
                continue
            if query_params.inviter_id is not None and inv.inviter_id != query_params.inviter_id:
                continue
            if query_params.status is not None and inv.status != query_params.status:
                continue
            invitations.append(inv)
        rows = embed_tags_on_invitations(invitations, tagging_repo, tag_repo)
        _attach_guest_slots(rows, guest_slot_repo)
        return rows
    raw = invitation_repo.list(_params_without_tag_filter(query_params))
    rows = embed_tags_on_invitations(raw, tagging_repo, tag_repo)
    _attach_guest_slots(rows, guest_slot_repo)
    return rows

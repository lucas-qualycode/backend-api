from application.taggings.embed import embed_tags_on_invitations
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


def list_invitations_as_dicts(
    invitation_repo: InvitationRepository,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
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
        return embed_tags_on_invitations(invitations, tagging_repo, tag_repo)
    raw = invitation_repo.list(_params_without_tag_filter(query_params))
    return embed_tags_on_invitations(raw, tagging_repo, tag_repo)

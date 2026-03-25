from application.taggings.embed import embed_tags_on_events
from domain.events.entity import Event, EventQueryParams
from domain.events.repository import EventRepository
from domain.tags.repository import TagRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def _params_without_tag_filter(q: EventQueryParams) -> EventQueryParams:
    return EventQueryParams(
        name=q.name,
        active=q.active,
        is_paid=q.is_paid,
        is_online=q.is_online,
        deleted=q.deleted,
        created_by=q.created_by,
        limit=q.limit,
        offset=q.offset,
    )


def list_events(repo: EventRepository, query_params: EventQueryParams) -> list[Event]:
    return repo.list(_params_without_tag_filter(query_params))


def list_events_as_dicts(
    event_repo: EventRepository,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
    query_params: EventQueryParams,
) -> list[dict]:
    if query_params.tag_id:
        rows = tagging_repo.list_by_tag(
            TaggingEntityType.EVENT,
            query_params.tag_id,
            query_params.limit,
            query_params.offset,
        )
        events: list[Event] = []
        for r in rows:
            ev = event_repo.get_by_id(r.entity_id)
            if ev is None or ev.deleted:
                continue
            if query_params.active is not None and ev.active != query_params.active:
                continue
            if query_params.is_paid is not None and ev.is_paid != query_params.is_paid:
                continue
            if query_params.is_online is not None and ev.is_online != query_params.is_online:
                continue
            if query_params.deleted is not None and ev.deleted != query_params.deleted:
                continue
            if query_params.created_by is not None and ev.created_by != query_params.created_by:
                continue
            if query_params.name is not None and ev.name != query_params.name:
                continue
            events.append(ev)
        return embed_tags_on_events(events, tagging_repo, tag_repo)
    raw = event_repo.list(_params_without_tag_filter(query_params))
    return embed_tags_on_events(raw, tagging_repo, tag_repo)

from domain.events.entity import Event
from domain.tags.entity import Tag
from domain.tags.repository import TagRepository
from domain.taggings.entity import Tagging
from domain.taggings.repository import TaggingRepository


def load_tags_by_ids(tag_repo: TagRepository, tag_ids: list[str]) -> dict[str, Tag]:
    out: dict[str, Tag] = {}
    for tid in tag_ids:
        t = tag_repo.get_by_id(tid)
        if t is not None and not t.deleted:
            out[tid] = t
    return out


def taggings_by_entity_id(taggings: list[Tagging]) -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    for tg in taggings:
        m.setdefault(tg.entity_id, []).append(tg.tag_id)
    return m


def embed_tags_on_events(
    events: list[Event],
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
) -> list[dict]:
    if not events:
        return []
    ids = [e.id for e in events]
    all_t = tagging_repo.list_for_entities("EVENT", ids)
    by_eid = taggings_by_entity_id(all_t)
    all_tag_ids = list({tid for tids in by_eid.values() for tid in tids})
    tag_map = load_tags_by_ids(tag_repo, all_tag_ids)
    rows: list[dict] = []
    for e in events:
        d = e.model_dump(mode="json")
        tids = by_eid.get(e.id, [])
        d["tags"] = [
            {
                "id": tag_map[tid].id,
                "name": tag_map[tid].name,
                "parent_tag_id": tag_map[tid].parent_tag_id,
            }
            for tid in tids
            if tid in tag_map
        ]
        rows.append(d)
    return rows


def embed_tags_on_event(
    event: Event,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
) -> dict:
    return embed_tags_on_events([event], tagging_repo, tag_repo)[0]


def embed_tags_on_products(products: list, tagging_repo: TaggingRepository, tag_repo: TagRepository) -> list[dict]:
    if not products:
        return []
    ids = [p.id for p in products]
    all_t = tagging_repo.list_for_entities("PRODUCT", ids)
    by_eid = taggings_by_entity_id(all_t)
    all_tag_ids = list({tid for tids in by_eid.values() for tid in tids})
    tag_map = load_tags_by_ids(tag_repo, all_tag_ids)
    rows: list[dict] = []
    for p in products:
        d = p.model_dump(mode="json")
        tids = by_eid.get(p.id, [])
        d["tags"] = [
            {
                "id": tag_map[tid].id,
                "name": tag_map[tid].name,
                "parent_tag_id": tag_map[tid].parent_tag_id,
            }
            for tid in tids
            if tid in tag_map
        ]
        rows.append(d)
    return rows


def embed_tags_on_product(product, tagging_repo: TaggingRepository, tag_repo: TagRepository) -> dict:
    return embed_tags_on_products([product], tagging_repo, tag_repo)[0]


def embed_tags_on_invitations(invitations: list, tagging_repo: TaggingRepository, tag_repo: TagRepository) -> list[dict]:
    if not invitations:
        return []
    ids = [i.id for i in invitations]
    all_t = tagging_repo.list_for_entities("INVITATION", ids)
    by_eid = taggings_by_entity_id(all_t)
    all_tag_ids = list({tid for tids in by_eid.values() for tid in tids})
    tag_map = load_tags_by_ids(tag_repo, all_tag_ids)
    rows: list[dict] = []
    for inv in invitations:
        d = inv.model_dump(mode="json")
        tids = by_eid.get(inv.id, [])
        d["tags"] = [
            {
                "id": tag_map[tid].id,
                "name": tag_map[tid].name,
                "parent_tag_id": tag_map[tid].parent_tag_id,
            }
            for tid in tids
            if tid in tag_map
        ]
        rows.append(d)
    return rows


def embed_tags_on_invitation(invitation, tagging_repo: TaggingRepository, tag_repo: TagRepository) -> dict:
    return embed_tags_on_invitations([invitation], tagging_repo, tag_repo)[0]

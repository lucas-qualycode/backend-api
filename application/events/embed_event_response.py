from application.locations.embed import embed_locations_on_event_dicts
from application.taggings.embed import embed_tags_on_event, embed_tags_on_events
from domain.events.entity import Event
from domain.locations.repository import LocationRepository
from domain.tags.repository import TagRepository
from domain.taggings.repository import TaggingRepository


def embed_event_response_dict(
    event: Event,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
    location_repo: LocationRepository,
) -> dict:
    d = embed_tags_on_event(event, tagging_repo, tag_repo)
    return embed_locations_on_event_dicts([d], location_repo)[0]


def embed_events_response_dicts(
    events: list[Event],
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
    location_repo: LocationRepository,
) -> list[dict]:
    rows = embed_tags_on_events(events, tagging_repo, tag_repo)
    return embed_locations_on_event_dicts(rows, location_repo)

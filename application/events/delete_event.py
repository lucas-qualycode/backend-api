from domain.events.entity import Event
from domain.events.exceptions import EventNotFoundError
from domain.events.repository import EventRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def delete_event(
    repo: EventRepository,
    tagging_repo: TaggingRepository,
    event_id: str,
    last_updated_by: str,
) -> Event:
    result = repo.soft_delete(event_id, last_updated_by)
    if result is None:
        raise EventNotFoundError(event_id)
    tagging_repo.delete_all_for_entity(TaggingEntityType.EVENT, event_id)
    return result

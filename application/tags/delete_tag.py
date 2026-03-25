from domain.tags.entity import Tag
from domain.tags.exceptions import TagNotFoundError
from domain.tags.repository import TagRepository


def delete_tag(
    repo: TagRepository,
    tag_id: str,
    last_updated_by: str,
) -> Tag:
    result = repo.soft_delete(tag_id, last_updated_by)
    if result is None:
        raise TagNotFoundError(tag_id)
    return result

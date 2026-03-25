from domain.tags.entity import Tag
from domain.tags.exceptions import TagNotFoundError
from domain.tags.repository import TagRepository


def get_tag(repo: TagRepository, tag_id: str) -> Tag:
    tag = repo.get_by_id(tag_id)
    if tag is None:
        raise TagNotFoundError(tag_id)
    return tag

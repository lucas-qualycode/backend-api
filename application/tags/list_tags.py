from domain.tags.entity import Tag, TagQueryParams
from domain.tags.repository import TagRepository


def list_tags(repo: TagRepository, query_params: TagQueryParams) -> list[Tag]:
    return repo.list(query_params)

from abc import ABC, abstractmethod

from domain.tags.entity import Tag, TagQueryParams


class TagRepository(ABC):
    @abstractmethod
    def create(self, tag: Tag) -> Tag:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Tag | None:
        ...

    @abstractmethod
    def list(self, query_params: TagQueryParams) -> list[Tag]:
        ...

    @abstractmethod
    def update(self, id: str, tag: Tag) -> Tag:
        ...

    @abstractmethod
    def soft_delete(self, id: str, last_updated_by: str) -> Tag | None:
        ...

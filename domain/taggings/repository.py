from abc import ABC, abstractmethod

from domain.taggings.entity import Tagging


class TaggingRepository(ABC):
    @abstractmethod
    def create(self, tagging: Tagging) -> Tagging:
        ...

    @abstractmethod
    def list_by_entity(self, entity_type: str, entity_id: str) -> list[Tagging]:
        ...

    @abstractmethod
    def list_by_tag(
        self,
        entity_type: str,
        tag_id: str,
        limit: int | None,
        offset: int | None,
    ) -> list[Tagging]:
        ...

    @abstractmethod
    def list_for_entities(self, entity_type: str, entity_ids: list[str]) -> list[Tagging]:
        ...

    @abstractmethod
    def delete_all_for_entity(self, entity_type: str, entity_id: str) -> None:
        ...

    @abstractmethod
    def replace_all_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        tag_ids: list[str],
        created_by: str,
        created_at: str,
    ) -> None:
        ...

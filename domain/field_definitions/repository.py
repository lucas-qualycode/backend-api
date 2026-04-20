from abc import ABC, abstractmethod

from domain.field_definitions.entity import FieldDefinition, FieldDefinitionQueryParams


class FieldDefinitionRepository(ABC):
    @abstractmethod
    def create(self, row: FieldDefinition) -> FieldDefinition:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> FieldDefinition | None:
        ...

    @abstractmethod
    def list(self, query_params: FieldDefinitionQueryParams) -> list[FieldDefinition]:
        ...

    @abstractmethod
    def update(self, id: str, row: FieldDefinition) -> FieldDefinition:
        ...

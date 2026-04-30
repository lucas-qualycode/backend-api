from abc import ABC, abstractmethod

from domain.invitations.entity import Invitation, InvitationQueryParams, InvitationStatus


class InvitationRepository(ABC):
    @abstractmethod
    def create(self, invitation: Invitation) -> Invitation:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> Invitation | None:
        ...

    @abstractmethod
    def list(self, query_params: InvitationQueryParams) -> list[Invitation]:
        ...

    @abstractmethod
    def update(self, id: str, invitation: Invitation) -> Invitation:
        ...

    @abstractmethod
    def update_status(self, id: str, status: InvitationStatus, metadata: dict | None) -> Invitation | None:
        ...

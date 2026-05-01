from abc import ABC, abstractmethod

from domain.invitation_guest_slots.entity import InvitationGuestSlot


class InvitationGuestSlotRepository(ABC):
    @abstractmethod
    def list_by_invitation_id(self, invitation_id: str) -> list[InvitationGuestSlot]:
        ...

    @abstractmethod
    def delete_all_for_invitation(self, invitation_id: str) -> None:
        ...

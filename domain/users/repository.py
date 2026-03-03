from abc import ABC, abstractmethod

from backend_api.domain.users.entity import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        ...

    @abstractmethod
    def get_by_id(self, id: str) -> User | None:
        ...

    @abstractmethod
    def update(self, id: str, user: User) -> User:
        ...

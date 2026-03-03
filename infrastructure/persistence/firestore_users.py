from typing import Any

from backend_api.domain.users.entity import User
from backend_api.domain.users.repository import UserRepository
from backend_api.infrastructure.config import USERS_COLLECTION_NAME


class FirestoreUserRepository(UserRepository):
    def __init__(self, db: Any, collection_name: str = USERS_COLLECTION_NAME) -> None:
        self._db = db
        self._coll = db.collection(collection_name)

    def _dump(self, user: User) -> dict[str, Any]:
        return user.model_dump(mode="json")

    def create(self, user: User) -> User:
        self._coll.document(user.id).set(self._dump(user))
        return user

    def get_by_id(self, id: str) -> User | None:
        doc = self._coll.document(id).get()
        if not doc.exists:
            return None
        return User.model_validate(doc.to_dict())

    def update(self, id: str, user: User) -> User:
        self._coll.document(id).update(self._dump(user))
        return user

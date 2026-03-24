from domain.users.entity import User
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository


def get_user(repo: UserRepository, user_id: str) -> User:
    user = repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user

from application.users.schemas import CreateUserInput
from domain.users.entity import User, UserPreferences
from domain.users.repository import UserRepository


def create_user(
    repo: UserRepository,
    data: CreateUserInput,
    now: str,
) -> User:
    if data.preferences is not None:
        base = UserPreferences().model_dump()
        base.update(data.preferences.model_dump(exclude_unset=True))
        prefs = UserPreferences(**base)
    else:
        prefs = UserPreferences()
    user = User(
        id=data.id,
        email=data.email,
        displayName=data.displayName,
        photoURL=data.photoURL,
        emailVerified=data.emailVerified,
        createdAt=now,
        updatedAt=now,
        phoneNumber=data.phoneNumber,
        preferences=prefs,
    )
    return repo.create(user)

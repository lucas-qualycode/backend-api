from backend_api.application.users.schemas import CreateUserInput
from backend_api.domain.users.entity import User, UserPreferences
from backend_api.domain.users.repository import UserRepository


def create_user(
    repo: UserRepository,
    data: CreateUserInput,
    now: str,
) -> User:
    prefs = None
    if data.preferences is not None:
        prefs = UserPreferences(
            notifications=data.preferences.notifications,
            language=data.preferences.language,
            timezone=data.preferences.timezone,
        )
    user = User(
        id=data.id,
        email=data.email,
        displayName=data.displayName,
        photoURL=data.photoURL,
        emailVerified=data.emailVerified,
        createdAt=now,
        updatedAt=now,
        phoneNumber=data.phoneNumber,
        preferences=prefs or UserPreferences(),
    )
    return repo.create(user)

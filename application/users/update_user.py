from backend_api.application.users.schemas import UpdateUserInput
from backend_api.domain.users.entity import User, UserPreferences
from backend_api.domain.users.exceptions import UserNotFoundError
from backend_api.domain.users.repository import UserRepository


def update_user(
    repo: UserRepository,
    user_id: str,
    data: UpdateUserInput,
    updated_at: str,
) -> User:
    existing = repo.get_by_id(user_id)
    if existing is None:
        raise UserNotFoundError(user_id)
    updates = data.model_dump(exclude_unset=True)
    if "preferences" in updates and updates["preferences"] is not None:
        p = updates["preferences"]
        updates["preferences"] = UserPreferences(
            notifications=p.get("notifications", True),
            language=p.get("language", "pt-BR"),
            timezone=p.get("timezone", "UTC-3"),
        )
    updated_user = existing.model_copy(update={**updates, "updatedAt": updated_at})
    return repo.update(user_id, updated_user)

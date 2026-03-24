from application.users.schemas import UpdateUserInput
from domain.users.entity import User, UserPreferences
from domain.users.exceptions import UserNotFoundError
from domain.users.repository import UserRepository


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
        base = existing.preferences.model_dump()
        if isinstance(p, dict):
            merged = {k: v for k, v in p.items() if v is not None}
        else:
            merged = p.model_dump(exclude_unset=True)
        allowed = set(UserPreferences.model_fields)
        base.update({k: v for k, v in merged.items() if k in allowed})
        updates["preferences"] = UserPreferences(**base)
    updated_user = existing.model_copy(update={**updates, "updatedAt": updated_at})
    return repo.update(user_id, updated_user)

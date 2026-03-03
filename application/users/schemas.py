from pydantic import BaseModel


class UserPreferencesInput(BaseModel):
    notifications: bool = True
    language: str = "en"
    timezone: str = "UTC"


class CreateUserInput(BaseModel):
    id: str
    email: str
    displayName: str | None = None
    photoURL: str | None = None
    emailVerified: bool = False
    phoneNumber: str | None = None
    preferences: UserPreferencesInput | None = None


class UpdateUserInput(BaseModel):
    email: str | None = None
    displayName: str | None = None
    photoURL: str | None = None
    emailVerified: bool | None = None
    phoneNumber: str | None = None
    preferences: UserPreferencesInput | None = None

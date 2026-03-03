from pydantic import BaseModel


class UserPreferences(BaseModel):
    notifications: bool = True
    language: str = "en"
    timezone: str = "UTC"


class User(BaseModel):
    id: str
    email: str
    displayName: str | None = None
    photoURL: str | None = None
    emailVerified: bool = False
    createdAt: str
    updatedAt: str
    phoneNumber: str | None = None
    preferences: UserPreferences = UserPreferences()

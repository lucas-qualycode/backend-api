from typing import Literal

from pydantic import BaseModel

ThemeMode = Literal["system", "light", "dark"]
Density = Literal["default", "compact", "comfortable"]
FontSizePref = Literal["standard", "large"]
ReducedMotion = Literal["system", "reduce", "full"]


class UserPreferencesInput(BaseModel):
    notifications: bool = True
    language: str = "pt-BR"
    timezone: str = "UTC-3"
    themeMode: ThemeMode = "system"
    density: Density = "default"
    fontSize: FontSizePref = "standard"
    reducedMotion: ReducedMotion = "system"


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

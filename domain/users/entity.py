from typing import Literal

from pydantic import BaseModel

ThemeMode = Literal["system", "light", "dark"]
Density = Literal["default", "compact", "comfortable"]
FontSizePref = Literal["standard", "large"]
ReducedMotion = Literal["system", "reduce", "full"]
LanguageCode = Literal["en", "pt-BR"]


class UserPreferences(BaseModel):
    notifications: bool = True
    language: LanguageCode = "pt-BR"
    timezone: str = "UTC-3"
    themeMode: ThemeMode = "system"
    density: Density = "default"
    fontSize: FontSizePref = "standard"
    reducedMotion: ReducedMotion = "system"


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

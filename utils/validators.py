import re

from domain.events.primary_categories import ALLOWED_EVENT_PRIMARY_CATEGORIES
from utils.errors import ValidationError

NAME_MAX_LENGTH = 256
URL_REGEX = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)


def validate_name(name: str | None, field: str = "name") -> None:
    if name is None:
        return
    if len(name) > NAME_MAX_LENGTH:
        raise ValidationError(f"{field} must be at most {NAME_MAX_LENGTH} characters")


def validate_url(value: str | None, field: str) -> None:
    if not value:
        return
    if not URL_REGEX.match(value):
        raise ValidationError(f"{field} must be a valid URL")


def validate_latitude(value: float | None) -> None:
    if value is None:
        return
    if value < -90 or value > 90:
        raise ValidationError("latitude must be between -90 and 90")


def validate_longitude(value: float | None) -> None:
    if value is None:
        return
    if value < -180 or value > 180:
        raise ValidationError("longitude must be between -180 and 180")


def validate_country_code(value: str | None) -> None:
    if value is None:
        return
    if len(value) != 2 or not value.isalpha():
        raise ValidationError("country must be a 2-letter ISO 3166-1 alpha-2 code")


def validate_primary_category(value: str | None) -> None:
    if value is None:
        return
    s = value.strip()
    if not s:
        raise ValidationError("primary_category must not be empty when provided")
    if s not in ALLOWED_EVENT_PRIMARY_CATEGORIES:
        raise ValidationError("invalid primary_category")

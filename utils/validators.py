import re
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

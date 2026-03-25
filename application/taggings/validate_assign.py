from domain.tags.repository import TagRepository
from utils.errors import ValidationError


def validate_tag_ids_for_entity(
    tag_repo: TagRepository,
    tag_ids: list[str],
    entity_type: str,
    *,
    require_at_least_one: bool,
) -> None:
    if require_at_least_one and not tag_ids:
        raise ValidationError("At least one tag is required")
    seen: set[str] = set()
    for tid in tag_ids:
        if tid in seen:
            raise ValidationError("Duplicate tags")
        seen.add(tid)
        tag = tag_repo.get_by_id(tid)
        if tag is None or tag.deleted or not tag.active:
            raise ValidationError(f"Invalid tag: {tid}")
        if entity_type not in tag.applies_to:
            raise ValidationError(f"Tag cannot be applied to this entity type: {tid}")

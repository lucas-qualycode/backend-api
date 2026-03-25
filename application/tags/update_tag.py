from application.tags.schemas import UpdateTagInput
from application.tags.validation import (
    assert_applies_to_compatible_with_parent,
    assert_child_name_differs_from_parent,
    assert_sibling_name_unique,
    refresh_descendant_depths,
    would_create_cycle,
)
from domain.tags.entity import Tag
from domain.tags.exceptions import TagNotFoundError
from domain.tags.repository import TagRepository
from utils.errors import ValidationError
from utils.validators import validate_name


def update_tag(
    repo: TagRepository,
    tag_id: str,
    data: UpdateTagInput,
    last_updated_by: str,
    updated_at: str,
) -> Tag:
    existing = repo.get_by_id(tag_id)
    if existing is None:
        raise TagNotFoundError(tag_id)
    updates = data.model_dump(exclude_unset=True)
    merged_name = updates["name"].strip() if "name" in updates else existing.name.strip()
    merged_parent_id = updates["parent_tag_id"] if "parent_tag_id" in updates else existing.parent_tag_id
    merged_applies = updates["applies_to"] if "applies_to" in updates else existing.applies_to
    merged_description = updates.get("description", existing.description)
    merged_active = updates["active"] if "active" in updates else existing.active
    validate_name(merged_name, "name")
    if not merged_name:
        raise ValidationError("name is required")
    if not merged_applies:
        raise ValidationError("applies_to must not be empty")
    parent: Tag | None = None
    if merged_parent_id is not None:
        parent = repo.get_by_id(merged_parent_id)
        if parent is None or parent.deleted:
            raise ValidationError("Invalid parent tag")
        assert_applies_to_compatible_with_parent(merged_applies, parent)
        assert_child_name_differs_from_parent(merged_name, parent)
    if "parent_tag_id" in updates:
        if would_create_cycle(repo, tag_id, merged_parent_id):
            raise ValidationError("Invalid parent tag: would create a cycle")
    if "name" in updates or "parent_tag_id" in updates:
        assert_sibling_name_unique(repo, merged_name, merged_parent_id, tag_id)
    if merged_parent_id is None:
        depth = 0
    else:
        depth = parent.depth + 1
    updated = Tag(
        id=existing.id,
        name=merged_name,
        description=merged_description,
        parent_tag_id=merged_parent_id,
        applies_to=list(merged_applies),
        depth=depth,
        active=merged_active,
        deleted=existing.deleted,
        created_at=existing.created_at,
        updated_at=updated_at,
        created_by=existing.created_by,
        last_updated_by=last_updated_by,
    )
    repo.update(tag_id, updated)
    stored = repo.get_by_id(tag_id)
    if stored is None:
        return updated
    if "parent_tag_id" in updates:
        refresh_descendant_depths(repo, stored, last_updated_by, updated_at)
        out = repo.get_by_id(tag_id)
        return out if out is not None else stored
    return stored

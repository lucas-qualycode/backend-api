import uuid

from application.tags.schemas import CreateTagInput
from application.tags.validation import (
    assert_applies_to_compatible_with_parent,
    assert_child_name_differs_from_parent,
    assert_sibling_name_unique,
)
from domain.tags.entity import Tag
from domain.tags.repository import TagRepository
from utils.errors import ValidationError
from utils.validators import validate_name


def create_tag(
    repo: TagRepository,
    data: CreateTagInput,
    created_by: str,
    now: str,
) -> Tag:
    validate_name(data.name, "name")
    if not data.name.strip():
        raise ValidationError("name is required")
    if not data.applies_to:
        raise ValidationError("applies_to must not be empty")
    parent: Tag | None = None
    if data.parent_tag_id is not None:
        parent = repo.get_by_id(data.parent_tag_id)
        if parent is None or parent.deleted or not parent.active:
            raise ValidationError("Invalid parent tag")
        assert_applies_to_compatible_with_parent(data.applies_to, parent)
        assert_child_name_differs_from_parent(data.name, parent)
    assert_sibling_name_unique(repo, data.name, data.parent_tag_id, None)
    depth = parent.depth + 1 if parent else 0
    tag = Tag(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        description=data.description,
        parent_tag_id=data.parent_tag_id,
        applies_to=list(data.applies_to),
        depth=depth,
        active=data.active,
        deleted=False,
        created_at=now,
        updated_at=now,
        created_by=created_by,
        last_updated_by=created_by,
    )
    return repo.create(tag)

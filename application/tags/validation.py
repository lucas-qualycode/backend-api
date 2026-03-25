from domain.tags.entity import Tag, TagQueryParams
from domain.tags.repository import TagRepository
from utils.errors import ValidationError


def assert_child_name_differs_from_parent(name: str, parent: Tag | None) -> None:
    if parent is None:
        return
    if name.strip().lower() == parent.name.strip().lower():
        raise ValidationError("Tag name must not be the same as the parent tag name")


def assert_sibling_name_unique(
    tag_repo: TagRepository,
    name: str,
    parent_tag_id: str | None,
    exclude_tag_id: str | None,
) -> None:
    normalized = name.strip().lower()
    if parent_tag_id is None:
        params = TagQueryParams(roots_only=True, deleted=False, limit=500, offset=0)
    else:
        params = TagQueryParams(parent_tag_id=parent_tag_id, deleted=False, limit=500, offset=0)
    for t in tag_repo.list(params):
        if exclude_tag_id is not None and t.id == exclude_tag_id:
            continue
        if t.name.strip().lower() == normalized:
            raise ValidationError("A tag with this name already exists under this parent")


def would_create_cycle(tag_repo: TagRepository, tag_id: str, new_parent_id: str | None) -> bool:
    if new_parent_id is None:
        return False
    cur: str | None = new_parent_id
    while cur is not None:
        if cur == tag_id:
            return True
        parent = tag_repo.get_by_id(cur)
        if parent is None:
            break
        cur = parent.parent_tag_id
    return False


def assert_applies_to_compatible_with_parent(
    child_applies_to: list[str],
    parent: Tag | None,
) -> None:
    if parent is None:
        return
    parent_set = set(parent.applies_to)
    for x in child_applies_to:
        if x not in parent_set:
            raise ValidationError("Tag applies_to must be a subset of the parent's applies_to")


def refresh_descendant_depths(
    tag_repo: TagRepository,
    parent: Tag,
    last_updated_by: str,
    updated_at: str,
) -> None:
    params = TagQueryParams(parent_tag_id=parent.id, deleted=False, limit=500, offset=0)
    children = tag_repo.list(params)
    for ch in children:
        new_depth = parent.depth + 1
        updated_child = ch.model_copy(
            update={
                "depth": new_depth,
                "updated_at": updated_at,
                "last_updated_by": last_updated_by,
            }
        )
        tag_repo.update(ch.id, updated_child)
        stored = tag_repo.get_by_id(ch.id)
        if stored is not None:
            refresh_descendant_depths(tag_repo, stored, last_updated_by, updated_at)

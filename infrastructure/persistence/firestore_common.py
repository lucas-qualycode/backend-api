from datetime import datetime
from typing import Any


def get_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def apply_filters(
    query: Any,
    params: Any,
    filters: list[tuple[str, str, str]],
) -> Any:
    for param_attr, field, op in filters:
        val = getattr(params, param_attr, None)
        if val is not None:
            query = query.where(field, op, getattr(val, "value", val))
    return query

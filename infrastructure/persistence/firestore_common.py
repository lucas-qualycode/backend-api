from datetime import datetime
from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter


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
            query = query.where(
                filter=FieldFilter(field, op, getattr(val, "value", val)),
            )
    return query

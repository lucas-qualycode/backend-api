from application.orders.schemas import OrderItemInput
from domain.field_definitions.entity import FieldType
from domain.field_definitions.exceptions import FieldDefinitionNotFoundError
from domain.field_definitions.repository import FieldDefinitionRepository
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository
from utils.errors import ValidationError


def _additional_data_list(item: OrderItemInput) -> list:
    if item.additional_data is not None:
        raw = item.additional_data
    elif item.metadata:
        raw = item.metadata.get("additional_data")
    else:
        raw = None
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValidationError("additional_data must be a list")
    return raw


def validate_order_items_additional_data(
    product_repo: ProductRepository,
    field_repo: FieldDefinitionRepository,
    items: list[OrderItemInput],
) -> None:
    for it in items:
        product = product_repo.get_by_id(it.product_id)
        if product is None:
            raise ProductNotFoundError(it.product_id)
        additional_list = _additional_data_list(it)
        effective_fields = _resolve_effective_fields(product.additional_info_fields, field_repo)
        if effective_fields:
            if len(additional_list) != it.quantity:
                raise ValidationError(
                    f"additional_data must have {it.quantity} entries for this line item"
                )
            for idx, entry in enumerate(additional_list):
                if not isinstance(entry, dict):
                    raise ValidationError(f"additional_data[{idx}] must be an object")
                _validate_single_entry(entry, effective_fields)
        elif len(additional_list) > 0:
            raise ValidationError("This product does not collect additional information")


def _resolve_effective_fields(refs: list, field_repo: FieldDefinitionRepository) -> list[dict]:
    resolved: list[dict] = []
    keys_seen: set[str] = set()
    for ref in refs:
        if ref.active is False:
            continue
        row = field_repo.get_by_id(ref.field_id)
        if row is None or row.deleted:
            raise FieldDefinitionNotFoundError(ref.field_id)
        if not row.active:
            raise ValidationError(f"Field definition is not active: {ref.field_id}")
        key = row.key
        if key in keys_seen:
            raise ValidationError(f"Duplicate field key in product refs: {key}")
        keys_seen.add(key)
        resolved.append(
            {
                "key": key,
                "field_type": row.field_type,
                "required": ref.required if ref.required is not None else row.required_default,
                "min_length": row.min_length,
                "max_length": row.max_length,
                "minimum": row.minimum,
                "maximum": row.maximum,
                "options": row.options,
            }
        )
    return resolved


def _validate_single_entry(entry: dict, fields: list[dict]) -> None:
    fields_by_key = {f["key"]: f for f in fields}
    for key, f in fields_by_key.items():
        if f["required"] and key not in entry:
            raise ValidationError(f"Missing required field: {key}")
    for key, value in entry.items():
        f = fields_by_key.get(key)
        if f is None:
            raise ValidationError(f"Unexpected field: {key}")
        _validate_value(key, value, f)


def _validate_value(key: str, value: object, field: dict) -> None:
    ft = field["field_type"]
    if ft == FieldType.TEXT:
        if not isinstance(value, str):
            raise ValidationError(f"Field {key} must be a string")
        min_length = field["min_length"]
        max_length = field["max_length"]
        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"Field {key} below min_length")
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"Field {key} exceeds max_length")
        return
    if ft == FieldType.NUMBER:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValidationError(f"Field {key} must be a number")
        minimum = field["minimum"]
        maximum = field["maximum"]
        if minimum is not None and value < minimum:
            raise ValidationError(f"Field {key} below minimum")
        if maximum is not None and value > maximum:
            raise ValidationError(f"Field {key} above maximum")
        return
    if ft == FieldType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValidationError(f"Field {key} must be a boolean")
        return
    if ft == FieldType.SELECT:
        if not isinstance(value, str):
            raise ValidationError(f"Field {key} must be a string")
        options = field["options"] or []
        if value not in options:
            raise ValidationError(f"Field {key} must be one of the allowed values")
        return
    raise ValidationError(f"Unsupported field_type for key {key}")

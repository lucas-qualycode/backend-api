from application.products.schemas import CreateProductInput, UpdateProductInput
from domain.products.entity import Product
from utils.errors import ValidationError
from utils.validators import validate_name


def validate_product_additional_info_fields_shape(
    refs: list[dict] | list[object],
) -> None:
    seen: set[str] = set()
    for idx, ref in enumerate(refs):
        field_id = getattr(ref, "field_id", None)
        if not isinstance(field_id, str) or not field_id.strip():
            raise ValidationError(f"additional_info_fields[{idx}].field_id is required")
        fid = field_id.strip()
        if fid in seen:
            raise ValidationError(f"additional_info_fields has duplicate field_id: {fid}")
        seen.add(fid)
        order = getattr(ref, "order", None)
        if order is not None and order < 0:
            raise ValidationError(f"additional_info_fields[{idx}].order must be >= 0")


def validate_product_create(data: CreateProductInput) -> None:
    if not data.name or not data.name.strip():
        raise ValidationError("name is required")
    validate_name(data.name, "name")
    if data.description is None or not str(data.description).strip():
        raise ValidationError("description is required")
    if data.is_free:
        if data.value != 0:
            raise ValidationError("value must be 0 when is_free is true")
    else:
        if data.value <= 0:
            raise ValidationError("value must be greater than 0 when is_free is false")
    if data.quantity <= 0:
        raise ValidationError("quantity must be a positive integer")
    if data.max_per_user <= 0:
        raise ValidationError("max_per_user must be a positive integer")
    validate_product_additional_info_fields_shape(data.additional_info_fields)


def validate_product_state(product: Product) -> None:
    if not product.name or not product.name.strip():
        raise ValidationError("name is required")
    validate_name(product.name, "name")
    if not product.description or not str(product.description).strip():
        raise ValidationError("description is required")
    if product.is_free:
        if product.value != 0:
            raise ValidationError("value must be 0 when is_free is true")
    else:
        if product.value <= 0:
            raise ValidationError("value must be greater than 0 when is_free is false")
    if product.quantity <= 0:
        raise ValidationError("quantity must be a positive integer")
    if product.max_per_user <= 0:
        raise ValidationError("max_per_user must be a positive integer")
    validate_product_additional_info_fields_shape(product.additional_info_fields)


def validate_product_update_patch(data: UpdateProductInput) -> None:
    if data.name is not None:
        if not data.name.strip():
            raise ValidationError("name cannot be empty")
        validate_name(data.name, "name")
    if data.description is not None and not str(data.description).strip():
        raise ValidationError("description cannot be empty")
    if data.quantity is not None and data.quantity <= 0:
        raise ValidationError("quantity must be a positive integer")
    if data.max_per_user is not None and data.max_per_user <= 0:
        raise ValidationError("max_per_user must be a positive integer")
    if data.additional_info_fields is not None:
        validate_product_additional_info_fields_shape(data.additional_info_fields)

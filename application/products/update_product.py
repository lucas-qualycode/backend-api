from application.products.schemas import UpdateProductInput
from domain.products.entity import Product
from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository


def update_product(
    repo: ProductRepository,
    product_id: str,
    data: UpdateProductInput,
    last_updated_by: str,
    updated_at: str,
) -> Product:
    existing = repo.get_by_id(product_id)
    if existing is None:
        raise ProductNotFoundError(product_id)
    updates = data.model_dump(exclude_unset=True)
    updated_product = existing.model_copy(
        update={**updates, "updated_at": updated_at, "last_updated_by": last_updated_by}
    )
    return repo.update(product_id, updated_product)

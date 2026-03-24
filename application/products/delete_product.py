from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository


def delete_product(repo: ProductRepository, product_id: str) -> None:
    existing = repo.get_by_id(product_id)
    if existing is None:
        raise ProductNotFoundError(product_id)
    repo.soft_delete(product_id)

from backend_api.domain.products.entity import Product
from backend_api.domain.products.exceptions import ProductNotFoundError
from backend_api.domain.products.repository import ProductRepository


def get_product(repo: ProductRepository, product_id: str) -> Product:
    product = repo.get_by_id(product_id)
    if product is None:
        raise ProductNotFoundError(product_id)
    return product

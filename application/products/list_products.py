from backend_api.domain.products.entity import Product, ProductQueryParams
from backend_api.domain.products.repository import ProductRepository


def list_products(
    repo: ProductRepository,
    query_params: ProductQueryParams,
) -> list[Product]:
    return repo.list(query_params)

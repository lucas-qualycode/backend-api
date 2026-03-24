from domain.products.entity import Product, ProductQueryParams
from domain.products.repository import ProductRepository


def list_products(
    repo: ProductRepository,
    query_params: ProductQueryParams,
) -> list[Product]:
    return repo.list(query_params)

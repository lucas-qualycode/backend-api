from domain.user_products.entity import UserProduct, UserProductQueryParams
from domain.user_products.repository import UserProductRepository


def list_user_products(
    repo: UserProductRepository,
    query_params: UserProductQueryParams,
) -> list[UserProduct]:
    return repo.list(query_params)

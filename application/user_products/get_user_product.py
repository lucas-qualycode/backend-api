from backend_api.domain.user_products.entity import UserProduct
from backend_api.domain.user_products.exceptions import UserProductNotFoundError
from backend_api.domain.user_products.repository import UserProductRepository


def get_user_product(repo: UserProductRepository, user_product_id: str) -> UserProduct:
    user_product = repo.get_by_id(user_product_id)
    if user_product is None:
        raise UserProductNotFoundError(user_product_id)
    return user_product

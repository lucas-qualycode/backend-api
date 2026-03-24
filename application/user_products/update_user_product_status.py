from domain.user_products.entity import UserProduct
from domain.user_products.exceptions import UserProductNotFoundError
from domain.user_products.repository import UserProductRepository


def update_user_product_status(
    repo: UserProductRepository,
    user_product_id: str,
    status: str,
) -> UserProduct:
    result = repo.update_status(user_product_id, status)
    if result is None:
        raise UserProductNotFoundError(user_product_id)
    return result

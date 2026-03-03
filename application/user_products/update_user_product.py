from backend_api.application.user_products.schemas import UpdateUserProductInput
from backend_api.domain.user_products.entity import UserProduct
from backend_api.domain.user_products.exceptions import UserProductNotFoundError
from backend_api.domain.user_products.repository import UserProductRepository


def update_user_product(
    repo: UserProductRepository,
    user_product_id: str,
    data: UpdateUserProductInput,
    updated_at: str,
) -> UserProduct:
    existing = repo.get_by_id(user_product_id)
    if existing is None:
        raise UserProductNotFoundError(user_product_id)
    updates = data.model_dump(exclude_unset=True)
    updated_user_product = existing.model_copy(update={**updates, "updated_at": updated_at})
    return repo.update(user_product_id, updated_user_product)

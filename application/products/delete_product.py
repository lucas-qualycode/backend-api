from domain.products.exceptions import ProductNotFoundError
from domain.products.repository import ProductRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def delete_product(
    repo: ProductRepository,
    tagging_repo: TaggingRepository,
    product_id: str,
) -> None:
    existing = repo.get_by_id(product_id)
    if existing is None:
        raise ProductNotFoundError(product_id)
    repo.soft_delete(product_id)
    tagging_repo.delete_all_for_entity(TaggingEntityType.PRODUCT, product_id)

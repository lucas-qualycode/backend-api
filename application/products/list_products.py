from application.products.embed_inventory import embed_inventory_on_product_dicts
from application.taggings.embed import embed_tags_on_products
from domain.inventory.repository import InventoryRepository
from domain.products.entity import Product, ProductQueryParams
from domain.products.repository import ProductRepository
from domain.tags.repository import TagRepository
from domain.taggings.entity import TaggingEntityType
from domain.taggings.repository import TaggingRepository


def _params_without_tag_filter(q: ProductQueryParams) -> ProductQueryParams:
    return ProductQueryParams(
        name=q.name,
        parent_id=q.parent_id,
        active=q.active,
        deleted=q.deleted,
        limit=q.limit,
        offset=q.offset,
    )


def list_products(
    repo: ProductRepository,
    query_params: ProductQueryParams,
) -> list[Product]:
    return repo.list(_params_without_tag_filter(query_params))


def list_products_as_dicts(
    product_repo: ProductRepository,
    tagging_repo: TaggingRepository,
    tag_repo: TagRepository,
    inventory_repo: InventoryRepository,
    query_params: ProductQueryParams,
) -> list[dict]:
    if query_params.tag_id:
        rows = tagging_repo.list_by_tag(
            TaggingEntityType.PRODUCT,
            query_params.tag_id,
            query_params.limit,
            query_params.offset,
        )
        products: list[Product] = []
        for r in rows:
            p = product_repo.get_by_id(r.entity_id)
            if p is None or p.deleted:
                continue
            if query_params.parent_id is not None and p.parent_id != query_params.parent_id:
                continue
            if query_params.active is not None and p.active != query_params.active:
                continue
            if query_params.deleted is not None and p.deleted != query_params.deleted:
                continue
            products.append(p)
        tagged = embed_tags_on_products(products, tagging_repo, tag_repo)
        return embed_inventory_on_product_dicts(tagged, inventory_repo)
    raw = product_repo.list(_params_without_tag_filter(query_params))
    tagged = embed_tags_on_products(raw, tagging_repo, tag_repo)
    return embed_inventory_on_product_dicts(tagged, inventory_repo)

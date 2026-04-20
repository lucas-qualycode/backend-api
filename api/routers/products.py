from fastapi import APIRouter, Depends, HTTPException

from api.auth import CurrentUser, RequireOrganizer
from api.deps import (
    get_db,
    get_inventory_repository,
    get_product_repository,
    get_tag_repository,
    get_tagging_repository,
)
from application.products import (
    create_product,
    delete_product,
    get_product,
    list_products_as_dicts,
    update_product,
)
from application.products.embed_inventory import embed_inventory_on_one_product_dict
from application.products.schemas import CreateProductInput, UpdateProductInput
from application.taggings import embed_tags_on_product, validate_tag_ids_for_entity
from domain.products.entity import ProductQueryParams
from domain.products.exceptions import ProductNotFoundError
from domain.products.types import ProductType
from domain.taggings.entity import TaggingEntityType
from infrastructure.persistence.firestore_common import get_timestamp
from utils.errors import ValidationError

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products_endpoint(
    name: str | None = None,
    parent_id: str | None = None,
    type: ProductType | None = None,
    active: bool | None = None,
    deleted: bool | None = None,
    tag_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    repo=Depends(get_product_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    inventory_repo=Depends(get_inventory_repository),
):
    params = ProductQueryParams(
        name=name,
        parent_id=parent_id,
        type=type,
        active=active,
        deleted=deleted,
        limit=limit,
        offset=offset,
        tag_id=tag_id,
    )
    return list_products_as_dicts(
        repo, tagging_repo, tag_repo, inventory_repo, params
    )


@router.get("/{id}")
def get_product_endpoint(
    id: str,
    repo=Depends(get_product_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    inventory_repo=Depends(get_inventory_repository),
):
    try:
        product = get_product(repo, id)
        row = embed_tags_on_product(product, tagging_repo, tag_repo)
        row = embed_inventory_on_one_product_dict(row, inventory_repo)
        return row
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", status_code=201)
def create_product_endpoint(
    data: CreateProductInput,
    current_user: CurrentUser = RequireOrganizer,
    db=Depends(get_db),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    inventory_repo=Depends(get_inventory_repository),
):
    try:
        validate_tag_ids_for_entity(
            tag_repo,
            data.tag_ids,
            TaggingEntityType.PRODUCT,
            require_at_least_one=False,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    now = get_timestamp()
    try:
        product = create_product(db, data, current_user.uid, now)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    tagging_repo.replace_all_for_entity(
        TaggingEntityType.PRODUCT,
        product.id,
        data.tag_ids,
        current_user.uid,
        now,
    )
    row = embed_tags_on_product(product, tagging_repo, tag_repo)
    return embed_inventory_on_one_product_dict(row, inventory_repo)


@router.put("/{id}")
@router.patch("/{id}")
def update_product_endpoint(
    id: str,
    data: UpdateProductInput,
    current_user: CurrentUser = RequireOrganizer,
    db=Depends(get_db),
    repo=Depends(get_product_repository),
    tagging_repo=Depends(get_tagging_repository),
    tag_repo=Depends(get_tag_repository),
    inventory_repo=Depends(get_inventory_repository),
):
    try:
        now = get_timestamp()
        try:
            product = update_product(db, repo, id, data, current_user.uid, now)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)
        if data.tag_ids is not None:
            try:
                validate_tag_ids_for_entity(
                    tag_repo,
                    data.tag_ids,
                    TaggingEntityType.PRODUCT,
                    require_at_least_one=False,
                )
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=e.message)
            tagging_repo.replace_all_for_entity(
                TaggingEntityType.PRODUCT,
                product.id,
                data.tag_ids,
                current_user.uid,
                now,
            )
        row = embed_tags_on_product(product, tagging_repo, tag_repo)
        return embed_inventory_on_one_product_dict(row, inventory_repo)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
def delete_product_endpoint(
    id: str,
    current_user: CurrentUser = RequireOrganizer,
    db=Depends(get_db),
    repo=Depends(get_product_repository),
    tagging_repo=Depends(get_tagging_repository),
):
    try:
        now = get_timestamp()
        delete_product(db, repo, tagging_repo, id, current_user.uid, now)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

PRODUCT_CATALOG_FIELD_NAMES = frozenset(
    {
        "name",
        "description",
        "imageURL",
        "parent_id",
        "parent_type",
        "type",
        "fulfillment_type",
        "fulfillment_profile_id",
        "additional_info_fields",
        "metadata",
    }
)
PRODUCT_COMMERCE_FIELD_NAMES = frozenset({"value", "is_free"})
PRODUCT_STOCK_FIELD_NAMES = frozenset({"quantity"})

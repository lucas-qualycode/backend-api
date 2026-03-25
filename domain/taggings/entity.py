from pydantic import BaseModel


class TaggingEntityType:
    EVENT = "EVENT"
    PRODUCT = "PRODUCT"
    INVITATION = "INVITATION"


class Tagging(BaseModel):
    id: str
    tag_id: str
    entity_type: str
    entity_id: str
    created_by: str
    created_at: str

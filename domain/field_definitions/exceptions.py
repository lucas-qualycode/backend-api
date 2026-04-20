class FieldDefinitionNotFoundError(Exception):
    def __init__(self, field_id: str) -> None:
        self.field_id = field_id
        super().__init__(f"Field definition not found: {field_id}")

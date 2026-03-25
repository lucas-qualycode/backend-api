class TagNotFoundError(Exception):
    def __init__(self, tag_id: str) -> None:
        self.tag_id = tag_id
        super().__init__(f"Tag not found: {tag_id}")

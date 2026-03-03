from typing import Any

_firestore_client: Any = None


def get_firestore_client(db: Any = None) -> Any:
    if db is not None:
        return db
    global _firestore_client
    if _firestore_client is None:
        import firebase_admin
        from firebase_admin import firestore
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        _firestore_client = firestore.client()
    return _firestore_client

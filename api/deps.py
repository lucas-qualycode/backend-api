from typing import Any

from fastapi import Depends

from infrastructure.firebase import get_firestore_client
from infrastructure.persistence.firestore_addresses import FirestoreAddressRepository
from infrastructure.persistence.firestore_attendees import FirestoreAttendeeRepository
from infrastructure.persistence.firestore_events import FirestoreEventRepository
from infrastructure.persistence.firestore_taggings import FirestoreTaggingRepository
from infrastructure.persistence.firestore_tags import FirestoreTagRepository
from infrastructure.persistence.firestore_locations import FirestoreLocationRepository
from infrastructure.persistence.firestore_invitations import FirestoreInvitationRepository
from infrastructure.persistence.firestore_inventory import FirestoreInventoryRepository
from infrastructure.persistence.firestore_orders import FirestoreOrderRepository
from infrastructure.persistence.firestore_payments import FirestorePaymentRepository
from infrastructure.persistence.firestore_products import FirestoreProductRepository
from infrastructure.persistence.firestore_schedules import FirestoreScheduleRepository
from infrastructure.persistence.firestore_stands import FirestoreStandRepository
from infrastructure.persistence.firestore_user_products import FirestoreUserProductRepository
from infrastructure.persistence.firestore_users import FirestoreUserRepository


def get_db() -> Any:
    return get_firestore_client()


def get_event_repository(db: Any = Depends(get_db)) -> FirestoreEventRepository:
    return FirestoreEventRepository(db)


def get_location_repository(db: Any = Depends(get_db)) -> FirestoreLocationRepository:
    return FirestoreLocationRepository(db)


def get_tag_repository(db: Any = Depends(get_db)) -> FirestoreTagRepository:
    return FirestoreTagRepository(db)


def get_tagging_repository(db: Any = Depends(get_db)) -> FirestoreTaggingRepository:
    return FirestoreTaggingRepository(db)


def get_stand_repository(db: Any = Depends(get_db)) -> FirestoreStandRepository:
    return FirestoreStandRepository(db)


def get_schedule_repository(db: Any = Depends(get_db)) -> FirestoreScheduleRepository:
    return FirestoreScheduleRepository(db)


def get_invitation_repository(db: Any = Depends(get_db)) -> FirestoreInvitationRepository:
    return FirestoreInvitationRepository(db)


def get_attendee_repository(db: Any = Depends(get_db)) -> FirestoreAttendeeRepository:
    return FirestoreAttendeeRepository(db)


def get_product_repository(db: Any = Depends(get_db)) -> FirestoreProductRepository:
    return FirestoreProductRepository(db)


def get_inventory_repository(db: Any = Depends(get_db)) -> FirestoreInventoryRepository:
    return FirestoreInventoryRepository(db)


def get_user_product_repository(db: Any = Depends(get_db)) -> FirestoreUserProductRepository:
    return FirestoreUserProductRepository(db)


def get_user_repository(db: Any = Depends(get_db)) -> FirestoreUserRepository:
    return FirestoreUserRepository(db)


def get_address_repository(db: Any = Depends(get_db)) -> FirestoreAddressRepository:
    return FirestoreAddressRepository(db)


def get_order_repository(db: Any = Depends(get_db)) -> FirestoreOrderRepository:
    return FirestoreOrderRepository(db)


def get_payment_repository(db: Any = Depends(get_db)) -> FirestorePaymentRepository:
    return FirestorePaymentRepository(db)

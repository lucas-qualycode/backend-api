from api.routers.addresses import router as addresses_router
from api.routers.attendees import router as attendees_router
from api.routers.events import router as events_router
from api.routers.locations import router as locations_router
from api.routers.invitations import router as invitations_router
from api.routers.orders import router as orders_router
from api.routers.payments import router as payments_router
from api.routers.products import router as products_router
from api.routers.schedules import router as schedules_router
from api.routers.tags import router as tags_router
from api.routers.stands import router as stands_router
from api.routers.user_products import router as user_products_router
from api.routers.users import router as users_router

__all__ = [
    "events_router",
    "locations_router",
    "tags_router",
    "stands_router",
    "schedules_router",
    "invitations_router",
    "attendees_router",
    "products_router",
    "user_products_router",
    "users_router",
    "addresses_router",
    "orders_router",
    "payments_router",
]

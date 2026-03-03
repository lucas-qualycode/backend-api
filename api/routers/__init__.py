from backend_api.api.routers.addresses import router as addresses_router
from backend_api.api.routers.attendees import router as attendees_router
from backend_api.api.routers.event_types import router as event_types_router
from backend_api.api.routers.events import router as events_router
from backend_api.api.routers.invitations import router as invitations_router
from backend_api.api.routers.orders import router as orders_router
from backend_api.api.routers.payments import router as payments_router
from backend_api.api.routers.products import router as products_router
from backend_api.api.routers.schedules import router as schedules_router
from backend_api.api.routers.stands import router as stands_router
from backend_api.api.routers.user_products import router as user_products_router
from backend_api.api.routers.users import router as users_router

__all__ = [
    "events_router",
    "event_types_router",
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

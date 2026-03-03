import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from backend_api.api.routers import (
    addresses_router,
    attendees_router,
    event_types_router,
    events_router,
    invitations_router,
    orders_router,
    payments_router,
    products_router,
    schedules_router,
    stands_router,
    user_products_router,
    users_router,
)
from backend_api.domain.addresses.exceptions import AddressNotFoundError
from backend_api.domain.attendees.exceptions import AttendeeNotFoundError
from backend_api.domain.event_types.exceptions import EventTypeNotFoundError
from backend_api.domain.events.exceptions import EventNotFoundError
from backend_api.domain.invitations.exceptions import InvitationNotFoundError
from backend_api.domain.orders.exceptions import OrderNotFoundError
from backend_api.domain.payments.exceptions import PaymentNotFoundError
from backend_api.domain.products.exceptions import ProductNotFoundError
from backend_api.domain.schedules.exceptions import ScheduleNotFoundError
from backend_api.domain.stands.exceptions import StandNotFoundError
from backend_api.domain.user_products.exceptions import UserProductNotFoundError
from backend_api.domain.users.exceptions import UserNotFoundError
from backend_api.utils.errors import NotFoundError, ValidationError

log = logging.getLogger("backend_api")

app = FastAPI(title="Event Social Media API")

app.include_router(events_router)
app.include_router(stands_router)
app.include_router(attendees_router)
app.include_router(event_types_router)
app.include_router(schedules_router)
app.include_router(invitations_router)
app.include_router(products_router)
app.include_router(user_products_router)
app.include_router(users_router)
app.include_router(addresses_router)
app.include_router(orders_router)
app.include_router(payments_router)


@app.get("/health")
def health():
    from datetime import datetime, timezone
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": exc.message})


@app.exception_handler(EventNotFoundError)
@app.exception_handler(EventTypeNotFoundError)
@app.exception_handler(StandNotFoundError)
@app.exception_handler(ScheduleNotFoundError)
@app.exception_handler(InvitationNotFoundError)
@app.exception_handler(AttendeeNotFoundError)
@app.exception_handler(ProductNotFoundError)
@app.exception_handler(UserProductNotFoundError)
@app.exception_handler(UserNotFoundError)
@app.exception_handler(AddressNotFoundError)
@app.exception_handler(OrderNotFoundError)
@app.exception_handler(PaymentNotFoundError)
async def handle_domain_not_found(request: Request, exc: Exception):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(ValidationError)
async def handle_validation(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"error": exc.message})


@app.exception_handler(PydanticValidationError)
async def handle_pydantic_validation(request: Request, exc: PydanticValidationError):
    return JSONResponse(status_code=400, content={"error": exc.errors()})


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    log.exception("Unexpected error")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})

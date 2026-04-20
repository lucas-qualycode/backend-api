# backend_api — FastAPI event platform API

This document is the complete reference for the **backend_api** repo: layout, conventions, auth, every endpoint, Firestore collections, exception handling, triggers, and how to extend it. **When changing backend_api** (new routes, auth, entities, repos, patterns, or libs), update this file so it stays accurate.

---

## Overview

- **Stack**: FastAPI, Firestore (Firebase), Firebase Auth. Python **3.12+** (`pyproject.toml`). Runs as HTTP API (e.g. via Mangum on Firebase Functions).
- **Role**: Event/social API: events, tickets, stands, schedules, invitations, attendees, user products, orders, payments, users, addresses.
- **Entry**: `main.py` wires the FastAPI app for Firebase; `app.py` defines the app and routers. Use `app` from module `app` (e.g. `uvicorn app:app`) with `PYTHONPATH` set to this directory for local runs or tests.
- **Health**: `GET /health` returns `{"status": "ok", "timestamp": "<ISO UTC>"}`. No auth.

---

## Architecture

The codebase follows a **layered (clean-style)** structure with clear dependency direction:

- **API (HTTP)** → **Application (use cases)** → **Domain** ← **Infrastructure**
- **Domain** has no dependencies on API or infrastructure: only Pydantic entities, abstract repository interfaces, and domain exceptions. It is the core.
- **Application** depends on domain and, where needed, **infrastructure config** and **Firestore transactions** for atomic multi-document writes. Most use cases still take only repositories; **product create/update/delete** uses `application/products/firestore_write.py` (Google Cloud Firestore `@transactional`) so `products` and `inventory` stay consistent.
- **API** depends on application and domain: routers parse HTTP, call application use cases, map exceptions to status codes. Uses FastAPI (`Depends`, `APIRouter`, etc.) and injects repositories via `api/deps.py`.
- **Infrastructure** depends on domain: Firestore repositories implement the abstract `*Repository` interfaces; `firestore_common` provides `get_timestamp` and `apply_filters`. No application or API imports.

Routers are thin (parse → call use case → return JSON). Business logic lives in the application layer; persistence details only in infrastructure.

---

## Patterns

- **Repository pattern**: Each aggregate has an abstract `*Repository` in `domain/<agg>/repository.py` (e.g. `get_by_id`, `list`, `create`, `update`) and a concrete `Firestore*Repository` in `infrastructure/persistence/`. Application and API depend on the interface, not the implementation.
- **Dependency injection**: FastAPI `Depends()` wires repositories and auth. All repo getters live in `api/deps.py` (e.g. `get_event_repository(db=Depends(get_db))`). Use cases receive repos as arguments, so they stay testable and framework-agnostic.
- **Use-case / application service**: One (or a few) functions per operation under `application/<agg>/` (e.g. `create_event`, `check_in_attendee`). They orchestrate domain and repositories; no HTTP or Firestore types.
- **Thin controllers**: Routers only validate auth, build query/body params, call one application function, and return `entity.model_dump(mode="json")` or list of same. Validation of input is via Pydantic (schemas in `application/*/schemas.py`) and optional domain validators in `utils/validators.py`.
- **Query params and filters**: List endpoints accept query params; these are mapped to `*QueryParams` models that have a `FILTER_SPEC` (param_attr, field, op) used by `apply_filters()` to build Firestore queries.

### Products and inventory

- **Product kind (`type`)**: **`TICKET`** \| **`MERCH`** (`domain.products.types.ProductType`). On Firestore read, missing or unknown `type` is normalized to **`MERCH`** (`Product._migrate_legacy_type`). Create/update bodies use the enum; list filter **`GET /products?type=`** accepts `TICKET` or `MERCH`. Inventory rows still use **`product_type`** `TICKET` vs `PRODUCT` (`InventoryProductType`); `MERCH` products map to inventory `PRODUCT`.
- **Fulfillment**: optional **`fulfillment_type`**: `DIGITAL` \| `WILL_CALL` \| `SHIPPING` \| `PICKUP`; optional **`fulfillment_profile_id`** for future profile documents. Checkout and fulfillment flows can branch on these instead of inferring from kind alone.
- **Catalog vs commerce vs stock (field grouping)**: **`domain.products.field_groups`** defines `PRODUCT_CATALOG_FIELD_NAMES` (presentation, kind, fulfillment, additional-info field refs, `metadata`), `PRODUCT_COMMERCE_FIELD_NAMES` (`value`, `is_free`), `PRODUCT_STOCK_FIELD_NAMES` (`quantity`). **Single source of truth for sellable quantity**: the **`inventory`** document (reserved vs available) is updated in the same transaction as **`products`** (`application/products/firestore_write.py`); `Product.quantity` is the line-of-record for total stock on the product and must stay aligned with inventory updates through those use cases—not ad hoc edits.
- **Product additional info fields**: products store **`additional_info_fields`** refs (`field_id` + optional `label`, `required`, `order`, `active`). `request_additional_info` remains for compatibility and is derived from whether refs are present.
- **Inventory document id**: **`PRODUCT_<productId>`** for every sellable product. The `inventory` document’s `product_type` field is `TICKET` or `PRODUCT` (see `domain/products/types.py`).
- **Create**: `create_product` validates input, sets `user_id` from the authenticated user (body does not accept `user_id`), builds `Product` + `InventoryItem`, then **one transaction** writes both collections.
- **Update**: Merged product is validated; transaction updates product and inventory; `available_quantity = max(0, new_total_quantity - reserved_quantity)` when quantity changes.
- **Delete**: Soft-delete product and deactivate inventory (`available_quantity = 0`, metadata) in one transaction, then remove product taggings.
- **API responses**: List/get/create/update product JSON includes **`inventory`**: `{ id, available_quantity, reserved_quantity, total_quantity }` or `null` if no row exists.
- **DI**: `get_inventory_repository` in `api/deps.py` wires `FirestoreInventoryRepository`.

### Field definitions

Field definitions are reusable documents in **`fieldDefinitions`** and can be attached to products. Each definition includes `key`, `label`, `field_type` (`text` \| `number` \| `boolean` \| `select`), default required flag, and optional constraints (`min_length`, `max_length`, `minimum`, `maximum`, `options`). Validation for create/update definitions is in `application/field_definitions/validation.py`.

### Orders and `additional_data`

On **`POST /orders`**, `application/orders/validate_additional_data.py` runs before persist: for each line item, load the product and resolve its `additional_info_fields` against field definitions. **`additional_data`** must be a list of length **`quantity`**; each entry must match resolved keys and type/constraint rules. If the product has no field refs, `additional_data` must be absent/empty. For transition compatibility, validation accepts legacy `metadata.additional_data` when `additional_data` is omitted. Payment approval reads `item.additional_data` first and falls back to legacy metadata, then copies per-unit values to **`UserProduct.additional_data`**.

---

## Main libraries

| Library | Purpose |
|--------|--------|
| **FastAPI** | Web framework: routing, `Depends` (DI), `APIRouter`, request/response, exception handlers. |
| **Pydantic** (v2) | Entity and schema models (`BaseModel`), validation, `model_dump(mode="json")`, `model_copy(update=...)`. |
| **firebase-admin** | Firebase Auth (`verify_id_token`), Firestore client (via project init). |
| **firebase-functions** | Deployment: HTTP function (`https_fn.on_request`), Firestore trigger (`on_document_written`). |
| **Mangum** | Adapter: AWS Lambda / API Gateway event → ASGI → FastAPI. Used in `main.py` to run the app in Firebase. |
| **uvicorn** | ASGI server for local development (`cd` into this directory, then `uvicorn app:app`; or `PYTHONPATH=<this_dir> uvicorn app:app`). |

Standard library usage: `hmac` (constant-time token compare for guest list), `secrets` (guest list token generation), `uuid` (new entity IDs), `datetime` (timestamps), `logging`.

---

## Directory layout

```
backend_api/
├── api/                    # HTTP layer
│   ├── auth.py             # get_current_user, get_optional_user, get_user_or_guest_list, require_roles, RequireOrganizer, RequireAdmin
│   ├── deps.py             # get_db, get_*_repository for every aggregate
│   └── routers/            # One router per domain (see API reference below)
├── application/            # Use cases per aggregate (events, attendees, orders, payments, …)
├── domain/                 # entity.py, repository.py (abstract), exceptions.py per aggregate
├── infrastructure/
│   ├── config.py           # Firestore collection names (see Collections below)
│   ├── firebase.py         # get_firestore_client()
│   └── persistence/        # firestore_common (get_timestamp, apply_filters), firestore_*.py repos
├── triggers/               # payment_approval: on_document_written("payments/{paymentId}")
├── utils/                  # errors (ValidationError, NotFoundError), validators (validate_name, validate_url, NAME_MAX_LENGTH, URL_REGEX)
├── app.py                  # FastAPI app, router includes, exception handlers
├── main.py                 # Firebase entry, Mangum handler
├── DEPLOY.md               # Firebase Functions deploy steps and frontend env
└── cursor.md               # This file
```

- **api/routers**: Thin HTTP: parse request, call application use case, return JSON. Auth via `Depends(get_current_user)`, `Depends(get_user_or_guest_list)`, or `RequireOrganizer` / `RequireAdmin`.
- **application/**: Use-case functions; take repo(s) and DTOs, return entities or raise domain exceptions. No FastAPI imports.
- **domain/**: Pydantic entities, `*QueryParams` with `FILTER_SPEC`, abstract `*Repository`, and domain exceptions.
- **infrastructure/persistence**: `get_timestamp()` (ISO UTC + "Z"), `apply_filters(query, params, FILTER_SPEC)`; each `Firestore*Repository` implements the corresponding `domain.*.repository`.

---

## Auth and authorization

- **Firebase ID token**: `Authorization: Bearer <id_token>`. Validated in `get_current_user`; returns `CurrentUser(uid, email, role)`. Role comes from token claims (e.g. custom `role`).
- **Guest list token**: For event-scoped read/check-in without a user. Header `X-Guest-List-Token` + path identifies event (`event_id` or `id`). Dependency `get_user_or_guest_list`:
  - Tries Bearer first; if valid, returns `UserOrGuestListAuth(user=CurrentUser(...), is_guest_list=False)`.
  - Else if `X-Guest-List-Token` present, loads event by path param, compares token to `event.guest_list_token` with `hmac.compare_digest`; on match returns `UserOrGuestListAuth(user=None, is_guest_list=True)`.
  - Otherwise 401.
- **Role checks**: `RequireOrganizer = Depends(require_roles("admin", "organizer"))`, `RequireAdmin = Depends(require_roles("admin"))`. Use on routes that need organizer or admin.
- **Routes using guest list**: `GET /events/{id}/user-products`, `GET /events/{event_id}/attendees`, `POST /events/{event_id}/attendees/check-in`. Check-in allows either Bearer (then must be admin/organizer) or valid guest list token.

---

## API reference (all endpoints)

Routers are mounted at root in `app.py`. Auth: **none** = no dependency; **user** = `get_current_user`; **optional user** = `get_optional_user`; **organizer** = `RequireOrganizer`; **user or guest** = `get_user_or_guest_list`; **guest check-in** = same + if user then must be admin/organizer.

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | none |
| **Events** (`prefix=/events`) | | |
| GET | `/events` | none |
| GET | `/events/{id}` | none |
| GET | `/events/{id}/user-products` | user or guest |
| POST | `/events/{id}/guest-list-token` | organizer |
| POST | `/events` | organizer |
| PUT/PATCH | `/events/{id}` | organizer |
| DELETE | `/events/{id}` | organizer (soft delete; no validate-deletion endpoint in FastAPI) |
| **Attendees** (under `/events`) | | |
| GET | `/events/{event_id}/attendees` | user or guest |
| GET | `/events/{event_id}/attendees/{id}` | user |
| POST | `/events/{event_id}/attendees` | user |
| POST | `/events/{event_id}/attendees/check-in` | guest check-in |
| PATCH | `/events/{event_id}/attendees/{id}/status` | user |
| **Stands** (under `/events`) | | |
| GET | `/events/{event_id}/stands` | user |
| GET | `/events/{event_id}/stands/{id}` | user |
| POST | `/events/{event_id}/stands` | organizer |
| PUT/PATCH | `/events/{event_id}/stands/{id}` | organizer |
| DELETE | `/events/{event_id}/stands/{id}` | organizer |
| **Tags** (`prefix=/tags`) | | |
| GET | `/tags` | none (query: active, deleted, parent_tag_id, applies_to, roots_only, limit, offset) |
| GET | `/tags/{id}` | none |
| POST | `/tags` | organizer |
| PUT/PATCH | `/tags/{id}` | organizer |
| DELETE | `/tags/{id}` | organizer |
| **Schedules** (`prefix=/schedules`) | | |
| GET | `/schedules` | organizer (**required** query `event_id`; caller must **own** the event) |
| GET | `/schedules/{id}` | organizer (schedule’s event must be **owned** by caller) |
| POST | `/schedules` | organizer (body `event_id` must be **owned**; `timezone` must be a valid **IANA** id; `status` one of `active` \| `cancelled` \| `completed`; dates `YYYY-MM-DD`, times `HH:mm`) |
| PUT/PATCH | `/schedules/{id}` | organizer (same ownership and validation rules on provided fields) |
| DELETE | `/schedules/{id}` | organizer (schedule’s event must be **owned** by caller) |
| **Invitations** (`prefix=/invitations`) | | |
| GET | `/invitations` | user (query: event_id, status, tag_id, limit, offset) |
| GET | `/invitations/{id}` | optional user (public or authenticated) |
| POST | `/invitations` | organizer |
| PUT/PATCH | `/invitations/{id}` | organizer |
| POST | `/invitations/{id}/status` | organizer |
| **Field definitions** (`prefix=/field-definitions`) | | |
| GET | `/field-definitions` | none (query: active, deleted, field_type, limit, offset) |
| GET | `/field-definitions/{id}` | none |
| POST | `/field-definitions` | organizer |
| PUT/PATCH | `/field-definitions/{id}` | organizer |
| **Products** (`prefix=/products`) | | |
| GET | `/products` | none (query: name, parent_id, active, deleted, tag_id, limit, offset) |
| GET | `/products/{id}` | none |
| POST | `/products` | organizer |
| PUT/PATCH | `/products/{id}` | organizer |
| DELETE | `/products/{id}` | organizer |
| **User products** (`prefix=/user-products`) | | |
| GET | `/user-products` | user |
| GET | `/user-products/{id}` | user |
| POST | `/user-products` | user |
| PUT/PATCH | `/user-products/{id}` | user |
| PATCH | `/user-products/{id}/status` | user |
| **Users** (`prefix=/users`) | | |
| POST | `/users` | user |
| GET | `/users/{id}` | user |
| PUT/PATCH | `/users/{id}` | user (see **Users** below for `preferences` merge) |
| **Addresses** (`prefix=/addresses`) | | |
| GET | `/addresses` | user (default filter by current user) |
| GET | `/addresses/{id}` | user |
| POST | `/addresses` | user |
| PUT/PATCH | `/addresses/{id}` | user |
| DELETE | `/addresses/{id}` | user |
| **Orders** (`prefix=/orders`) | | |
| GET | `/orders` | user |
| GET | `/orders/{id}` | user |
| POST | `/orders` | user (each line item: `additional_data` is validated per product field refs — see **Orders and additional_data** below) |
| PUT/PATCH | `/orders/{id}` | user |
| PATCH | `/orders/{id}/status` | user |
| **Payments** (`prefix=/payments`) | | |
| GET | `/payments` | user |
| GET | `/payments/{id}` | user |
| POST | `/payments` | user |
| PUT/PATCH | `/payments/{id}` | user |
| PATCH | `/payments/{id}/status` | user |

**Public (no auth)**: `/health`, `GET /events`, `GET /events/{id}`, `GET /tags`, `GET /tags/{id}`, `GET /products`, `GET /products/{id}`. **Optional auth**: `GET /invitations/{id}`.

### Users (`/users`)

- **User** (`domain/users/entity.py`): `id`, `email`, `displayName`, `photoURL`, `emailVerified`, `createdAt`, `updatedAt`, `phoneNumber`, **`preferences`**.
- **UserPreferences**: `notifications` (bool), `language`, `timezone`, **`themeMode`** (`system` \| `light` \| `dark`), **`density`** (`default` \| `compact` \| `comfortable`), **`fontSize`** (`standard` \| `large`), **`reducedMotion`** (`system` \| `reduce` \| `full`).
- **PATCH/PUT partial updates**: When the body includes `preferences`, the API **merges** into the existing `UserPreferences` instead of replacing the whole object with missing fields: only provided keys are applied on top of the stored preferences (`application/users/update_user.py`). Omit `preferences` to leave them unchanged.

---

## Firestore collections

Defined in `infrastructure/config.py`. Top-level: `events`, `tags`, `taggings`, `products`, `fieldDefinitions`, `userProducts`, `inventory`, `users`, `addresses`, `orders`, `payments`. Subcollections: under `events/{eventId}` → `stands`, `schedules`, `invitations`, `attendees`. Names: `EVENTS_COLLECTION_NAME` = `"events"`, `TAGS_COLLECTION_NAME` = `"tags"`, `TAGGINGS_COLLECTION_NAME` = `"taggings"`, `STANDS_COLLECTION_NAME` = `"stands"`, `SCHEDULES_COLLECTION_NAME` = `"schedules"`, `INVITATIONS_COLLECTION_NAME` = `"invitations"`, `ATTENDEES_COLLECTION_NAME` = `"attendees"`, `PRODUCTS_COLLECTION_NAME` = `"products"`, `FIELD_DEFINITIONS_COLLECTION_NAME` = `"fieldDefinitions"`, `USER_PRODUCTS_COLLECTION_NAME` = `"userProducts"`, `INVENTORY_COLLECTION_NAME` = `"inventory"`, `USERS_COLLECTION_NAME` = `"users"`, `ADDRESSES_COLLECTION_NAME` = `"addresses"`, `ORDERS_COLLECTION_NAME` = `"orders"`, `PAYMENTS_COLLECTION_NAME` = `"payments"`.

Composite index definitions for `tags` / `taggings` live in [`firestore.indexes.json`](firestore.indexes.json) in this directory (and in [`backend/firestore.indexes.json`](../backend/firestore.indexes.json) for the wider Firebase project).

---

## Exception handling (app.py)

- **404**: `NotFoundError` (content `{"error": exc.message}`); and each domain not-found: `EventNotFoundError`, `TagNotFoundError`, `StandNotFoundError`, `ScheduleNotFoundError`, `InvitationNotFoundError`, `AttendeeNotFoundError`, `ProductNotFoundError`, `UserProductNotFoundError`, `UserNotFoundError`, `FieldDefinitionNotFoundError`, `AddressNotFoundError`, `OrderNotFoundError`, `PaymentNotFoundError` (content `{"error": str(exc)}`).
- **400**: `ValidationError` → `{"error": exc.message}`; Pydantic validation → `{"error": exc.errors()}`.
- **500**: Any other exception → `{"error": "Internal server error"}` (and logged).

Success responses: single entity or list of entities as JSON (`model_dump(mode="json")`). Create endpoints often return 201 with the created resource; DELETE may return 204 (e.g. products, schedules, addresses) or 200 with body.

---

## Conventions

- **No comments in code** (per project rule); rely on clear names and this doc.
- **Use ipdb** for debugging: `import ipdb; ipdb.set_trace();`
- **Errors**: Domain exceptions in `domain/<agg>/exceptions.py` (e.g. `EventNotFoundError`). App-level `NotFoundError`/`ValidationError` in `utils/errors.py`. `app.py` maps them to 404/400; domain not-found types are also mapped to 404.
- **Repositories**: Abstract interface in `domain/<agg>/repository.py`; implementation in `infrastructure/persistence/firestore_<agg>.py`. Inject via `api/deps.py` (e.g. `get_event_repository`) and use in application layer.
- **Timestamps**: `get_timestamp()` from `infrastructure.persistence.firestore_common` returns ISO UTC strings; use for `created_at`, `updated_at`, `check_in_time`, etc.
- **IDs**: UUIDs for new entities (e.g. `str(uuid.uuid4())`); event/aggregate ids from path or body as appropriate.

---

## Adding a new feature

1. **Domain**: Add or extend entity and `*QueryParams` in `domain/<agg>/entity.py`; add exception in `domain/<agg>/exceptions.py`; extend or add abstract repo in `domain/<agg>/repository.py`.
2. **Infrastructure**: Implement or extend `Firestore*Repository` in `infrastructure/persistence/`, and add collection name in `infrastructure/config.py` if new collection.
3. **Application**: Add use-case module under `application/<agg>/` (e.g. `do_something.py`), export from `application/<agg>/__init__.py`.
4. **API**: In `api/deps.py` add `get_<agg>_repository` if new repo. In the right router, add endpoint: parse input, call use case, return JSON or raise; use `Depends(get_current_user)` or `get_user_or_guest_list` (and optionally `RequireOrganizer`) as needed.
5. **Exception handling**: If new domain exception should return 404/400, register it in `app.py` exception handlers (or use existing `NotFoundError`/`ValidationError`).

---

## Triggers

- **Payment approval** (`triggers/payment_approval.py`): Firestore trigger `on_document_written(document="payments/{paymentId}")`. Runs only when payment status transitions from non-APPROVED to APPROVED. Calls `process_payment_approval` (in `application/payments/process_payment_approval.py`) with payment, order, product, user_product, and invitation repos: creates user products from order items, updates inventory, and if order has `metadata.invitation_id` updates invitation to ACCEPTED (unless DECLINED). See `.cursor/rules/backend-business-rules.mdc` for full business flow.

---

## Domain entities (reference)

Each aggregate has `domain/<agg>/entity.py`: **Event** (id, name, description, location, active, is_paid, is_online, imageURL, deleted, created_at, updated_at, created_by, last_updated_by, guest_list_token); tags are attached via **Tagging** rows (`taggings` collection) and returned on event GET/list as embedded `tags`. **Tag** (hierarchical taxonomy: `parent_tag_id`, `applies_to`, `depth`, …); **Tagging** (id, tag_id, entity_type, entity_id, created_by, created_at). **Attendee** (id, event_id, user_id, user_product_id, invitation_id, status, check_in_time, created_at, updated_at, metadata); **UserProduct** (id, parent_id, product_id, user_id, status, quantity, price, currency, purchase_date, valid_from, valid_until, …); **Product**, **Order**, **Payment**, **Invitation**, **Stand**, **Schedule**, **User** (includes **UserPreferences** with appearance fields as above), **Address**. Query params live in the same entity file with a `FILTER_SPEC` class attribute for Firestore filters where applicable. Exceptions: `domain/<agg>/exceptions.py` (e.g. `EventNotFoundError(event_id)`).

---

## Configuration and run

- **Firestore**: Collection names in `infrastructure/config.py`. Client from `infrastructure.firebase.get_firestore_client()`. Firebase Admin is initialized in `main.py` when not already initialized.
- **Local**: From this directory, `PYTHONPATH=. uvicorn app:app --reload`. For Firebase emulator, use `make run` in this folder (imports/exports `firestore-snapshot`) or the entry point that mounts `main.api`. Imports use a flat layout (`application`, `domain`, `api`, …) so Cloud Functions deploy matches the filesystem.
- **Production deploy**: Firebase Cloud Functions from this directory: `make deploy` or `firebase deploy --only functions`. Requires Blaze and Firebase CLI; see [`DEPLOY.md`](DEPLOY.md). After deploy, set `VITE_API_URL` in react-frontend to the Functions URL for `api`.
- **Business rules**: Validations, status transitions, and domain rules are in `.cursor/rules/backend-business-rules.mdc` at the repo root; keep code and that doc aligned. Event delete is soft-delete only; there is no `validate-deletion` endpoint.

---

## Reference: event and guest list

- **Event** has optional `guest_list_token` (set via `POST /events/{id}/guest-list-token`). Used only for guest-list auth comparison; not returned in normal event GET.
- **GET /events/{id}/user-products**: List user products with `parent_id=id`, `status=ACTIVE`; auth = user or guest list.
- **POST /events/{id}/guest-list-token**: Generate token, set on event, return `{ "token": "..." }`; RequireOrganizer.
- **GET /events/{event_id}/attendees**: List attendees; `user_id` default = current user if Bearer, else unset (guest list sees all).
- **POST /events/{event_id}/attendees/check-in**: Body `{ "user_product_id": "..." }`. Resolve event and user product; if attendee exists and is CHECKED_IN return it; else update to CHECKED_IN with `check_in_time` or create new attendee with CHECKED_IN. Auth: user (admin/organizer) or guest list.

This file is the single source of truth for backend_api structure and behavior; update it when you add or change modules or auth.

# Deploy Firebase Cloud Functions (`backend_api`)

## Prerequisites

- **Firebase CLI** (`npm i -g firebase-tools` or use `npx firebase`).
- **`firebase login`** with an account that can deploy to the project in [`.firebaserc`](.firebaserc) (default: `partiiu-app`).
- **Blaze (pay-as-you-go)** on the Firebase project. Cloud Functions (2nd gen) need Cloud Build and Artifact Registry; Firebase will prompt to upgrade if the project is on Spark only. Upgrade: [Firebase usage / billing](https://console.firebase.google.com/project/partiiu-app/usage/details).

## Deploy

From this directory:

```bash
make deploy
```

or:

```bash
firebase deploy --only functions
```

This deploys the HTTP function `api` ([`main.py`](main.py)). The codebase uses flat imports (`app`, `application`, `domain`, `api`, …) so the deployed artifact matches how Python resolves modules at `/workspace`.

Deploy only named functions (optional):

```bash
firebase deploy --only functions:api
```

## After a successful deploy

1. Open **Firebase Console → Build → Functions** and copy the **HTTPS URL** for `api` (region and hostname depend on Firebase; copy the value shown there).
2. Set **`VITE_API_URL`** in the react-frontend environment to that base URL (no trailing slash required; see [`react-frontend/.env.example`](../react-frontend/.env.example)). Rebuild or redeploy the frontend so clients call the live API.

## Secrets (Mercado Pago) — production

Production uses **Secret Manager** + `secrets=[...]` in `main.py`. The app still reads:

```python
os.environ["MERCADOPAGO_ACCESS_TOKEN"]
```

### Critical: do not put the token in `.env` when deploying

On deploy, the Firebase CLI loads **`backend_api/.env`** and sets those keys as **plain** (non-secret) environment variables on Cloud Run.

If `MERCADOPAGO_ACCESS_TOKEN` is in `.env` **and** you bind it as a secret in `main.py`, Cloud Run returns:

```text
Secret environment variable overlaps non secret environment variable: MERCADOPAGO_ACCESS_TOKEN
```

Deploy may fail, or the plain (often empty) value wins — then the app reports **"Mercado Pago is not configured"** even though the secret exists in Secret Manager.

**Do this instead:**

| Environment | Where to put `MERCADOPAGO_ACCESS_TOKEN` |
|-------------|----------------------------------------|
| **Local** (emulator / uvicorn) | **`.env.local`** (not deployed; see [`.env.example`](.env.example)) |
| **Production** | **Secret Manager only** — `firebase functions:secrets:set MERCADOPAGO_ACCESS_TOKEN` |

Steps:

1. **Remove** `MERCADOPAGO_ACCESS_TOKEN` from `backend_api/.env` (if present).
2. **Local dev:** copy [`.env.example`](.env.example) to **`.env.local`** and set your `APP_USR-...` token there.
3. **Production secret** (once): `firebase functions:secrets:set MERCADOPAGO_ACCESS_TOKEN`
4. Grant access (if needed): `firebase functions:secrets:access MERCADOPAGO_ACCESS_TOKEN`
5. Ensure `main.py` has `secrets=[MERCADOPAGO_ACCESS_TOKEN]` on `@https_fn.on_request`.
6. **Redeploy:** `firebase deploy --only functions`

Verify the secret exists:

```bash
firebase functions:secrets:describe MERCADOPAGO_ACCESS_TOKEN
```

After deploy, check logs do **not** show the overlap error:

```bash
firebase functions:log --only api
```

In the function config you should see `secretEnvironmentVariables` with `key: MERCADOPAGO_ACCESS_TOKEN` and **no** duplicate plain env var with the same name.

## Repo shortcuts

- Root Makefile: `make python-back-deploy` runs `cd backend_api && make deploy`.

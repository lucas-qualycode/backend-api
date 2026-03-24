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

This deploys the HTTP function `api` ([`main.py`](main.py)) and the Firestore trigger `on_payment_status_changed` (imported from [`triggers/payment_approval.py`](triggers/payment_approval.py)). The codebase uses flat imports (`app`, `application`, `domain`, `api`, …) so the deployed artifact matches how Python resolves modules at `/workspace`.

Deploy only named functions (optional):

```bash
firebase deploy --only functions:api,functions:on_payment_status_changed
```

## After a successful deploy

1. Open **Firebase Console → Build → Functions** and copy the **HTTPS URL** for `api` (region and hostname depend on Firebase; copy the value shown there).
2. Set **`VITE_API_URL`** in the react-frontend environment to that base URL (no trailing slash required; see [`react-frontend/.env.example`](../react-frontend/.env.example)). Rebuild or redeploy the frontend so clients call the live API.

## Repo shortcuts

- Root Makefile: `make python-back-deploy` runs `cd backend_api && make deploy`.

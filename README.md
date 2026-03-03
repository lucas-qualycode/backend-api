# Backend API (FastAPI)

Run with the Firebase emulator (standalone, no other backend):

```bash
cd backend_api
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
firebase emulators:start --only functions
```

Then call the API at the URL shown (e.g. `http://127.0.0.1:5001/event-social-media-b879d/us-central1/api`). All routes are under that path (e.g. `.../api/health`, `.../api/events`).

Optional: use the same Firestore as the Node backend by starting the Firestore emulator from the `backend` folder and setting env when running the API locally with uvicorn:

```bash
FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 GCLOUD_PROJECT=event-social-media-b879d uvicorn backend_api.app:app --reload --host 0.0.0.0 --port 8000
```

(From repo root with `PYTHONPATH=.` or after `pip install -e .` from repo root.)

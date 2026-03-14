# Backend API (FastAPI)

Run with the Firebase emulator:

```bash
cd backend_api
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
make run
```

Then call the API at the URL shown (e.g. `http://127.0.0.1:5001/.../api`). All routes are under that path (e.g. `.../api/health`, `.../api/events`).

To run the API locally against the emulator (Auth, Firestore, Functions):

```bash
FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 GCLOUD_PROJECT=event-social-media-b879d PYTHONPATH=. uvicorn backend_api.app:app --reload --host 0.0.0.0 --port 8000
```

From repo root.

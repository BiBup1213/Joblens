# Joblens

JobLens is a lightweight dashboard for collecting job postings from different sources, analyzing them, and comparing them against a personal profile.

## Structure

```text
backend/   Django REST API
frontend/  React/Vite dashboard
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the backend URL from `VITE_API_BASE_URL`. For local development, copy `frontend/.env.example` to `frontend/.env` or use the default `http://127.0.0.1:8000/api`.

Build:

```bash
cd frontend
npm run build
```

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

The API is served under `/api/`. Local CORS is configured for Vite on `http://localhost:5173` and `http://127.0.0.1:5173`.

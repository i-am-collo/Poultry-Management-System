# Poultry Management System

This project contains:

- `backend/`: FastAPI API (auth + farmer/supplier/buyer APIs)
- `frontend/`: static HTML/JS dashboards and auth pages

## Backend Run

From `backend/`:

```powershell
.\poultry\Scripts\python -m uvicorn app.main:app --reload --port 8001
```

## Frontend Run

Open `frontend/index.html` with a static file server (recommended) so relative scripts and API calls work consistently.

## Tests (Step 4)

Backend tests are in `backend/tests` and use Python `unittest` with in-memory SQLite.

From `backend/`:

```powershell
.\poultry\Scripts\python -m unittest discover -s tests -v
```

## Deployment Readiness (Step 5)

1. Copy backend env template and set secrets:

```powershell
cd backend
Copy-Item .env.example .env
```

2. Edit `.env` and set at minimum:
- `APP_ENV=production` (for production)
- `SECRET_KEY=<long-random-secret>`
- `DATABASE_URL=<production-db-url>`

3. Run preflight checks:

```powershell
.\poultry\Scripts\python scripts\preflight.py
```

4. Optional container build:

```powershell
cd backend
docker build -t poultry-management-api .
docker run --env-file .env -p 8001:8001 poultry-management-api
```

## Implemented API Groups

- Auth: `/auth/*`
- Farmer: `/farmers/register-flock`, `/farmers/flocks`
- Supplier: `/suppliers/products`
- Buyer: `/buyers/search`, `/buyers/orders`

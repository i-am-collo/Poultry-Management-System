# Poultry Management System - AI Agent Instructions

## System Overview

**Architecture**: FastAPI (Python) backend + vanilla JavaScript frontend, connected via REST API with JWT authentication.

**Purpose**: Supply chain platform for poultry farmers, suppliers, and buyers to manage flocks, inventory, orders, and logistics.

**Key Technologies**: 
- Backend: FastAPI, SQLAlchemy ORM, PostgreSQL (production)
- Frontend: vanilla JavaScript, localStorage for session state
- Auth: JWT tokens, bcrypt password hashing, role-based access control (RBAC)

---

## Architecture Essentials

### Request Flow
1. **Frontend** (HTML+JS) → **APIClient** (centralized fetch wrapper) → **Backend** (FastAPI routes)
2. **Auth**: JWT token in `Authorization: Bearer <token>` header + `X-Role` header for role verification
3. **Response**: JSON with optional `detail` field for errors; frontend catches non-200 responses

### Data Model & Roles
- **User Roles**: `farmer`, `supplier`, `buyer`, `admin` (enum in [models.py](../backend/models.py#L10))
- **Core Entities**: 
  - `User`: accounts with role, status, created_at/updated_at timestamps
  - `Flock`: farmer-managed batches (breed, age_weeks, start_date)
  - `Order`: buyer→farmer/supplier transactions with status enum
  - `SupplierProduct`: inventory with pricing and availability
  - `Notification`: system messages for all roles
- **20+ tables**: See [models.py](../backend/models.py) for full schema

### API Structure
Backend routes in [main.py](../backend/main.py):
- `/auth` (login/logout) → [auth.py](../backend/auth.py)
- `/farmers` → [farmers.py](../backend/farmers.py) — flock registration, feed tracking, production logging
- `/suppliers` → [suppliers.py](../backend/suppliers.py) — product catalog, inventory management
- `/buyers` → [buyers.py](../backend/buyers.py) — search, orders
- `/orders`, `/inventory`, `/notifications`, `/reports`, `/admin`, `/health`

**Middleware**: CORS with origin whitelist from [config.py](../backend/config.py); security headers via nginx

---

## Critical Workflows

### Local Development
```bash
# Backend (terminal 1)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Frontend (terminal 2)
cd frontend
python -m http.server 3000  # Or use Live Server VS Code extension
# Browse http://localhost:3000
```

### Production Deployment
```bash
docker-compose up -d
# Starts FastAPI, PostgreSQL, nginx reverse proxy (port 80/443)
```

### Testing API
- **Swagger UI**: http://localhost:8000/docs (auto-generated, read-only)
- **Quick test**: Use [API_QUICK_REFERENCE.js](../frontend/API_QUICK_REFERENCE.js) for endpoint signatures

---

## Project-Specific Conventions

### Authentication Flow
1. User submits email+password on [login.html](../frontend/login.html)
2. [auth.js](../frontend/auth.js) calls `api.auth.login()` → POST `/auth/login`
3. Backend returns `{token, user, roles}`
4. Frontend stores token in `localStorage.setItem('token', ...)` and role in `localStorage.setItem('userRole', ...)`
5. [api-client.js](../frontend/api-client.js) auto-injects both in all subsequent requests

### API Response Patterns
- **Success**: `{data: {...}, message: "..."}`
- **Error**: `{detail: "error message"}` (HTTP 400/401/403/500 status)
- **Frontend catches** `!response.ok` and throws with `error.detail || response.status`

### State Management (Frontend)
- **No framework** (vanilla JS): localStorage for session/user data, DOM manipulation for UI
- **User object stored**: `{email, roles, id, ...}` in localStorage['user']
- **Re-login flow**: Check token before dashboard redirect; if missing, send to login.html

### Database Timestamps
- Model fields: `created_at = Column(DateTime, default=datetime.utcnow)`
- Always use `datetime.utcnow()` for UTC consistency (not system local time)
- `updated_at = Column(..., onupdate=datetime.utcnow)` for auto-update on save

### Environment Configuration
- Backend uses [config.py](../backend/config.py) with `pydantic-settings` (reads `.env` or defaults)
- Key vars: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS`, `ADMIN_PASSWORD`
- **Never commit `.env`** (in .gitignore); use `.env.example` template instead

### Database Migrations
- Schema: SQLAlchemy declarative models in [models.py](../backend/models.py)
- Initial setup: `Base.metadata.create_all(bind=engine)` in [main.py](../backend/main.py#L14)
- Production: Use Alembic (configured but not required for MVP)

---

## Integration Points & External Dependencies

### Role-Based Access
- Verify in frontend: `localStorage.getItem('userRole')` before rendering role-specific dashboards
- Verify in backend: Route dependencies enforce role via `X-Role` header check (see [security.py](../backend/security.py) if exists)

### Email/Notifications
- [notifications.py](../backend/notifications.py) provides API, but email sending **not yet configured** (stub implementation)
- To enable: Configure SMTP in config.py + add email library (`python-jose`, `email-validator` already in requirements.txt)

### Files/Uploads
- Currently **no file upload endpoints** (static assets only)
- To add: Use FastAPI's `UploadFile` + configure storage (local disk or S3)

### Logging
- Backend: Use Python `logging` module or FastAPI's built-in request logging
- Frontend: Browser console (no external logging service)
- Audit: DB stores `created_at`/`updated_at` for all entities; no detailed audit log yet

---

## Common Patterns

**API Client Usage** (frontend):
```javascript
// api-client.js instantiates APIClient globally as 'api'
// Usage pattern:
try {
    const result = await api.farmer.registerFlock({...});
    console.log(result);
} catch (error) {
    console.error(error.message);
}
```

**FastAPI Route Pattern** (backend):
```python
from fastapi import APIRouter, Depends, HTTPException
from database import get_db

router = APIRouter()

@router.post("/endpoint")
def create_item(item: ItemSchema, db: Session = Depends(get_db)):
    db_item = Model(**item.dict())
    db.add(db_item)
    db.commit()
    return db_item
```

**Form Submission** (frontend):
- Listen for `DOMContentLoaded` in each HTML file
- Get form via `getElementById()`, attach `submit` event, prevent default, call API
- Disable button during request; re-enable on error; redirect on success
- See [auth.js](../frontend/auth.js) as template

---

## Debugging Tips

1. **Backend errors**: Check FastAPI logs in terminal; use Swagger UI (`/docs`) to test endpoints
2. **CORS failures**: Verify frontend origin is in `ALLOWED_ORIGINS` in [config.py](../backend/config.py)
3. **Auth failures**: Check token expiry; inspect `Authorization` header in browser DevTools
4. **DB connection**: Test `DATABASE_URL` from `.env` (PostgreSQL format: `postgresql://user:pass@host/db`)
5. **Frontend state**: Inspect `localStorage` in DevTools to confirm token/user stored correctly

---

## Key Files to Understand First

1. [backend/main.py](../backend/main.py) — App initialization, route registration, CORS setup
2. [backend/models.py](../backend/models.py) — Data schema (User, Flock, Order, etc.)
3. [frontend/api-client.js](../frontend/api-client.js) — HTTP wrapper with auth injection
4. [frontend/auth.js](../frontend/auth.js) — Login form handler
5. [frontend/scripts.js](../frontend/scripts.js) — Role-based dashboard setup, role data
6. [backend/config.py](../backend/config.py) — Environment settings
7. [ARCHITECTURE.md](../ARCHITECTURE.md) — Visual system diagram

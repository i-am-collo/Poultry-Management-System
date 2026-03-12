from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.buyers import router as buyers_router
from app.api.farmers import router as farmers_router
from app.api.suppliers import router as suppliers_router
from app.api.notifications import router as notifications_router
from app.db.database import Base, engine
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("🚀 Starting up Poultry Management System API...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")
    yield
    print("🛑 Shutting down...")


app = FastAPI(
    title="Poultry Management System API",
    version="1.0.0",
    lifespan=lifespan,
)

# ════════════════════════════════════════════
# CORS MIDDLEWARE (MUST BE FIRST)
# ════════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (can be restricted to specific domains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ════════════════════════════════════════════
# API ROUTERS
# ════════════════════════════════════════════
app.include_router(auth_router)
app.include_router(farmers_router)
app.include_router(suppliers_router)
app.include_router(buyers_router)
app.include_router(notifications_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Poultry Management System API is running"}

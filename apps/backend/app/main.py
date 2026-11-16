"""
NeighbourNode API — Unified FastAPI entry point.
MongoDB-only architecture for CSAEC59 (AEC-NoSQL, Ramaiah Institute of Technology).
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_mongodb_service, get_telegram_service
from app.api.routes import (
    ai,
    analytics,
    auth,
    borrow,
    community,
    health,
    items,
    notifications,
    recommendations,
    resources,
    reviews,
    skill_requests,
    skills,
    users,
)
from app.api.routes.orchestrator import router as orchestrator_router
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.jobs.overdue_checker import OverdueChecker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("neighbournode")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NeighbourNode API...")
    await connect_to_mongo()

    settings = get_settings()
    telegram_service = get_telegram_service()
    mongodb_service = get_mongodb_service()

    checker = OverdueChecker(settings, telegram_service, mongodb_service)
    checker.start()
    app.state.overdue_checker = checker

    yield

    # Shutdown
    logger.info("Shutting down NeighbourNode API...")
    if hasattr(app.state, "overdue_checker") and app.state.overdue_checker:
        app.state.overdue_checker.shutdown()
    await close_mongo_connection()


app = FastAPI(
    title="NeighbourNode API",
    description="Smart Community Resource & Skill Sharing Platform — MongoDB NoSQL Project (CSAEC59, Ramaiah Institute of Technology)",
    version="2.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Versioned API (/api/v1) ─────────────────────────────────────
api_v1 = FastAPI(title="NeighbourNode API v1")
api_v1.include_router(auth.router)
api_v1.include_router(users.router)
api_v1.include_router(resources.router)
api_v1.include_router(skills.router)
api_v1.include_router(borrow.router)
api_v1.include_router(skill_requests.router)
api_v1.include_router(community.router)
api_v1.include_router(reviews.router)
api_v1.include_router(recommendations.router)
api_v1.include_router(notifications.router)
api_v1.include_router(analytics.router)
api_v1.include_router(ai.router)
api_v1.include_router(health.router)

app.mount("/api/v1", api_v1)

# ─── Top-level & Backwards Compatible Routers ────────────────────
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(borrow.router, prefix="/api")
app.include_router(skill_requests.router, prefix="/api")
app.include_router(community.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(orchestrator_router, prefix="/api")
app.include_router(telegram_router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "service": "NeighbourNode API",
        "version": "2.0.0",
        "database": "MongoDB ONLY",
        "course": "CSAEC59 — AEC-NoSQL",
        "institution": "Ramaiah Institute of Technology, Bengaluru",
        "status": "online",
        "docs_url": "/docs",
    }

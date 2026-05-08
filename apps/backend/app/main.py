"""
NeighbourNode API — single FastAPI entry point.

Merged from Member 2 and Member 3. Registers ALL route groups.
Starts the OverdueChecker background job on startup.
"""
from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root (app/main.py → app → backend → apps → repo root)
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_supabase_service, get_telegram_service
from app.api.routes import borrow, items, users
from app.api.routes.orchestrator import router as orchestrator_router
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings
from app.jobs.overdue_checker import OverdueChecker


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="NeighbourNode API")

# ─── CORS (allow Next.js frontend) ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Route registration ─────────────────────────────────────────
app.include_router(items.router)
app.include_router(borrow.router)
app.include_router(users.router)
app.include_router(telegram_router)
app.include_router(orchestrator_router)


@app.get("/")
def read_root():
    return {"message": "NeighbourNode API is running"}


# ─── Lifecycle ───────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    telegram_service = get_telegram_service()
    supabase_service = get_supabase_service()
    checker = OverdueChecker(settings, telegram_service, supabase_service)
    checker.start()
    app.state.overdue_checker = checker


@app.on_event("shutdown")
async def shutdown() -> None:
    checker = getattr(app.state, "overdue_checker", None)
    if checker:
        checker.shutdown()

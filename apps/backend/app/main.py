<<<<<<< HEAD
from fastapi import FastAPI
from app.api.routes import items, borrow, users

app = FastAPI(title="NeighbourNode API")

app.include_router(items.router)
app.include_router(borrow.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "NeighbourNode API is running"}
=======
from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.dependencies import get_supabase_service, get_telegram_service
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings
from app.jobs.overdue_checker import OverdueChecker


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="NeighbourNode")
app.include_router(telegram_router)


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
>>>>>>> 9923707 (Implement Telegram integration with calendar and notification services)

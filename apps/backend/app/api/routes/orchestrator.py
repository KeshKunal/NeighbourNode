"""
Orchestrator route — Portal-First entry point for borrow requests.

POST /api/orchestrate/borrow
POST /api/orchestrate/ask
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.agents.orchestrator import NeighbourOrchestrator
from app.agents.matchmaker.agent import run_matchmaker
from app.api.dependencies import get_mongodb_service, get_telegram_service
from app.schemas.api import BorrowByNameRequest, BorrowRequest, BorrowResponse
from app.services.mongodb_service import MongoDBService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orchestrate", tags=["orchestrator"])


@router.post("/borrow", response_model=BorrowResponse)
async def orchestrate_borrow(
    payload: BorrowRequest,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
    telegram_svc: TelegramService = Depends(get_telegram_service),
) -> BorrowResponse:
    orchestrator = NeighbourOrchestrator(
        mongodb_service=mongodb_svc,
        telegram_service=telegram_svc,
    )
    try:
        result = await orchestrator.process_portal_request(payload)
        return result
    except Exception:
        logger.exception("orchestrate.borrow.failed")
        raise HTTPException(status_code=500, detail="Orchestrator pipeline failed")


@router.post("/ask", response_model=BorrowResponse)
async def ask_matchmaker(
    payload: BorrowByNameRequest,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
    telegram_svc: TelegramService = Depends(get_telegram_service),
) -> BorrowResponse:
    try:
        state = {
            "item_name": payload.item_name,
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "user_id": payload.borrower_id,
        }
        match_result = await run_matchmaker(state, mongodb_svc)
        if not match_result.get("success") or not match_result.get("item_id"):
            return BorrowResponse(
                success=False,
                message=match_result.get("reason") or f"Could not find a match for '{payload.item_name}' nearby.",
            )

        orchestrator = NeighbourOrchestrator(
            mongodb_service=mongodb_svc,
            telegram_service=telegram_svc,
        )
        return await orchestrator.process_portal_request(
            BorrowRequest(
                item_id=match_result["item_id"],
                borrower_id=payload.borrower_id,
                requested_start=payload.requested_start,
                requested_end=payload.requested_end,
            )
        )
    except Exception:
        logger.exception("orchestrate.ask.failed")
        raise HTTPException(status_code=500, detail="AI Matchmaker pipeline failed")

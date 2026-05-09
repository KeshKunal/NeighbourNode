"""
Orchestrator route — Portal-First entry point for borrow requests.

POST /api/orchestrate/borrow
  The React portal calls this when a user clicks "Request" on an item.
  Input:  BorrowRequest (item_id, borrower_id, requested_start, requested_end)
  Output: BorrowResponse (success, transaction_id, message)

Flow:
  1. Instantiates NeighbourOrchestrator with live services
  2. Calls process_portal_request() which:
     - Validates item exists & is available
     - Creates PENDING_APPROVAL transaction (database lock)
     - Looks up owner's telegram_chat_id
     - Pushes approval notification to owner via Telegram
     - Returns success so the portal shows "Request Sent to Owner!"
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.agents.orchestrator import NeighbourOrchestrator
from app.api.dependencies import get_supabase_service, get_telegram_service
from app.schemas.api import BorrowRequest, BorrowResponse
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/orchestrate", tags=["orchestrator"])


@router.post("/borrow", response_model=BorrowResponse)
async def orchestrate_borrow(
    payload: BorrowRequest,
    supabase_svc: SupabaseService = Depends(get_supabase_service),
    telegram_svc: TelegramService = Depends(get_telegram_service),
) -> BorrowResponse:
    """
    Portal-First Golden Path:
    User clicks "Request" on the React catalog → this route fires →
    Orchestrator validates + locks + notifies owner on Telegram →
    Portal gets back a success response with the transaction_id.
    """
    orchestrator = NeighbourOrchestrator(
        supabase_service=supabase_svc,
        telegram_service=telegram_svc,
    )

    try:
        result = await orchestrator.process_portal_request(payload)
    except Exception:
        logger.exception("orchestrate.borrow.failed")
        raise HTTPException(status_code=500, detail="Orchestrator pipeline failed")

    return result

"""
Orchestrator route — the entry point for agent-driven borrow requests.

POST /api/orchestrate/borrow
  Accepts an item_name, runs the Matchmaker → Scavenger pipeline,
  and returns the result (match + transaction, or scavenger listings).
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.agents.orchestrator import run_orchestrator
from app.agents.state import OrchestrationState
from app.api.dependencies import get_supabase_service, get_telegram_service
from app.schemas.api import BorrowByNameRequest, BorrowResponse
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/orchestrate", tags=["orchestrator"])


@router.post("/borrow", response_model=BorrowResponse)
async def orchestrate_borrow(
    payload: BorrowByNameRequest,
    supabase_svc: SupabaseService = Depends(get_supabase_service),
    telegram_svc: TelegramService = Depends(get_telegram_service),
) -> BorrowResponse:
    """
    Agent-driven borrow: user says "I need a power drill" →
    Matchmaker searches Supabase → creates transaction → sends Telegram
    approval to owner.  If no match, Scavenger returns external listings.
    """
    state: OrchestrationState = {
        "user_id": payload.borrower_id,
        "item_name": payload.item_name,
        "requested_start": payload.requested_start.isoformat(),
        "requested_end": payload.requested_end.isoformat(),
        "status": "new",
        "errors": [],
    }

    try:
        result = await run_orchestrator(state, supabase_svc, telegram_svc)
    except Exception:
        logger.exception("orchestrate.borrow.failed")
        raise HTTPException(status_code=500, detail="Orchestrator pipeline failed")

    if result.get("errors"):
        logger.warning("orchestrate.borrow.errors", extra={"errors": result["errors"]})

    match = result.get("match_result")
    if match and match.get("success"):
        return BorrowResponse(
            success=True,
            transaction_id=result.get("transaction_id"),
            message=(
                f"Match found! Approval request sent to owner. "
                f"Transaction {result.get('transaction_id')} is PENDING_APPROVAL."
            ),
        )

    scavenger = result.get("scavenger_results", [])
    if scavenger:
        return BorrowResponse(
            success=False,
            message=(
                f"No local match for '{payload.item_name}'. "
                f"Found {len(scavenger)} external listing(s)."
            ),
        )

    return BorrowResponse(
        success=False,
        message=f"No matches found for '{payload.item_name}' locally or externally.",
    )

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
from app.schemas.api import BorrowRequest, BorrowResponse, BorrowByNameRequest
from app.agents.matchmaker.agent import run_matchmaker
from app.schemas.transaction import TransactionStatus
from app.schemas.telegram import BorrowApprovalMessage
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


@router.post("/ask", response_model=BorrowResponse)
async def ask_matchmaker(
    payload: BorrowByNameRequest,
    supabase_svc: SupabaseService = Depends(get_supabase_service),
    telegram_svc: TelegramService = Depends(get_telegram_service),
) -> BorrowResponse:
    """
    AI Chatbot Flow:
    User asks for an item by name → Matchmaker agent searches and picks the best match →
    Validates + locks + notifies owner on Telegram →
    Portal gets back a success response.
    """
    try:
        state = {
            "item_name": payload.item_name,
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "user_id": payload.borrower_id,
        }
        
        # 1. Run Matchmaker Agent
        match_result = await run_matchmaker(state, supabase_svc)
        
        if not match_result.get("success") or not match_result.get("item_id"):
            return BorrowResponse(
                success=False,
                message=match_result.get("reason") or f"Could not find a match for '{payload.item_name}' nearby.",
            )
            
        item_id = match_result["item_id"]
        owner_id = match_result["owner_id"]
        item_name = match_result["item_name"]
        owner_chat_id = match_result["owner_telegram_chat_id"]
        
        # 2. Database Lock — create PENDING_APPROVAL tx
        tx_data = {
            "item_id": item_id,
            "borrower_id": payload.borrower_id,
            "owner_id": owner_id,
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "status": TransactionStatus.PENDING_APPROVAL.value,
        }
        tx_rows = supabase_svc.create_transaction(tx_data)
        if not tx_rows:
            return BorrowResponse(
                success=False,
                message="Match found, but failed to create transaction. Please try again.",
            )
            
        transaction_id = tx_rows[0]["id"]
        
        # 3. Push Notification
        if owner_chat_id:
            borrower = supabase_svc.get_user_by_id(payload.borrower_id)
            borrower_name = borrower.get("full_name") if borrower else None
            
            approval_msg = BorrowApprovalMessage(
                transaction_id=transaction_id,
                owner_chat_id=int(owner_chat_id),
                item_name=item_name,
                borrower_name=borrower_name,
                requested_start=payload.requested_start,
                requested_end=payload.requested_end,
            )
            await telegram_svc.send_borrow_approval(approval_msg)
            
        return BorrowResponse(
            success=True,
            transaction_id=transaction_id,
            message=f"I found a {item_name}! The owner has been notified and we're waiting for their approval.",
        )
        
    except Exception:
        logger.exception("orchestrate.ask.failed")
        raise HTTPException(status_code=500, detail="AI Matchmaker pipeline failed")


"""
Orchestrator — the top-level agent pipeline.

Flow:
  1. Run Matchmaker (queries Supabase for matches)
  2. If match found:
     - Create transaction (PENDING_APPROVAL)
     - Send Telegram approval to owner
  3. If no match:
     - Run Scavenger (external search)
"""
from __future__ import annotations

import logging
from datetime import datetime

from app.schemas.telegram import BorrowApprovalMessage
from app.schemas.transaction import TransactionStatus
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService

from .matchmaker.agent import run_matchmaker
from .scavenger.agent import run_scavenger
from .state import MatchmakerResult, OrchestrationState


logger = logging.getLogger(__name__)


async def run_orchestrator(
    state: OrchestrationState,
    supabase_svc: SupabaseService,
    telegram_svc: TelegramService,
) -> OrchestrationState:
    """
    Main orchestration pipeline. Accepts live service instances so that
    agent actions (DB writes, Telegram messages) happen for real.
    """

    # ── Step 1: Matchmaker ──────────────────────────────────────
    match_result: MatchmakerResult = await run_matchmaker(state, supabase_svc)
    state["match_result"] = match_result

    if not match_result.get("success"):
        # ── Step 2a: Scavenger fallback ─────────────────────────
        logger.info("orchestrator.matchmaker.no_match — triggering scavenger")
        scavenger_result = await run_scavenger(state)
        state["scavenger_results"] = scavenger_result.get("results", [])
        return state

    # ── Step 2b: Match found — create transaction + notify ──────
    item_id = match_result.get("item_id")
    owner_id = match_result.get("owner_id")
    owner_chat_id = match_result.get("owner_telegram_chat_id")
    item_name = match_result.get("item_name") or state["item_name"]

    if not item_id or not owner_id:
        state["errors"].append("Matchmaker returned success but missing item_id/owner_id")
        return state

    state["item_id"] = item_id
    state["owner_id"] = owner_id

    # Create a PENDING_APPROVAL transaction in Supabase
    tx_data = {
        "item_id": item_id,
        "borrower_id": state["user_id"],
        "owner_id": owner_id,
        "requested_start": state["requested_start"],
        "requested_end": state["requested_end"],
        "status": TransactionStatus.PENDING_APPROVAL.value,
    }
    tx_rows = supabase_svc.create_transaction(tx_data)
    if not tx_rows:
        state["errors"].append("Failed to create transaction in Supabase")
        return state

    transaction_id = tx_rows[0]["id"]
    state["transaction_id"] = transaction_id
    state["status"] = TransactionStatus.PENDING_APPROVAL.value

    logger.info(
        "orchestrator.transaction.created",
        extra={"transaction_id": transaction_id, "item_id": item_id},
    )

    # Send Telegram approval request to owner
    if owner_chat_id:
        req_start = _safe_parse_dt(state["requested_start"])
        req_end = _safe_parse_dt(state["requested_end"])

        approval_msg = BorrowApprovalMessage(
            transaction_id=transaction_id,
            owner_chat_id=int(owner_chat_id),
            item_name=item_name,
            borrower_name=None,  # could look up borrower name if needed
            requested_start=req_start,
            requested_end=req_end,
        )
        send_result = await telegram_svc.send_borrow_approval(approval_msg)
        if send_result.ok and send_result.message_id:
            state["telegram_message_id"] = str(send_result.message_id)

        logger.info(
            "orchestrator.telegram.approval_sent",
            extra={
                "transaction_id": transaction_id,
                "owner_chat_id": owner_chat_id,
                "ok": send_result.ok,
            },
        )
    else:
        state["errors"].append("Owner has no telegram_chat_id — cannot send approval")

    return state


def _safe_parse_dt(value: str) -> datetime | None:
    """Best-effort ISO parse; return None on failure."""
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None

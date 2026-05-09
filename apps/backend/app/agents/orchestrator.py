"""
NeighbourOrchestrator — the Portal-First request pipeline.

Architecture:
  Portal (React) is the Source of Truth for browsing & requesting.
  Telegram is the Push-Notification & Fast-Action channel.

Golden Path (process_portal_request):
  1. Fetch item details from Supabase (validate it exists & is available)
  2. Create transaction with status=PENDING_APPROVAL (database lock)
  3. Look up the owner's telegram_chat_id
  4. Push an approval notification to the owner via Telegram
  5. Return success to the portal so the UI shows "Request Sent!"

The owner's Approve/Decline action comes back asynchronously through
the Telegram webhook (api/routes/telegram.py).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.schemas.api import BorrowRequest, BorrowResponse
from app.schemas.telegram import BorrowApprovalMessage
from app.schemas.transaction import TransactionStatus
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)


@dataclass
class NeighbourOrchestrator:
    """
    Wires the React Portal to Supabase and Telegram.

    Injected via FastAPI Depends — not a singleton, one instance per request.
    """
    supabase_service: SupabaseService
    telegram_service: TelegramService

    async def process_portal_request(self, payload: BorrowRequest) -> BorrowResponse:
        """
        Execute the synchronous Golden Path:
        Fetch → Lock → Lookup → Notify → Return.
        """
        item_id = payload.item_id
        borrower_id = payload.borrower_id

        # ── Step 1: Fetch the item ──────────────────────────────────
        item = self.supabase_service.get_item(item_id)
        if not item:
            logger.warning("orchestrator.item_not_found", extra={"item_id": item_id})
            return BorrowResponse(
                success=False,
                message=f"Item {item_id} not found.",
            )

        if item.get("current_status") != TransactionStatus.AVAILABLE.value:
            logger.info(
                "orchestrator.item_unavailable",
                extra={"item_id": item_id, "status": item.get("current_status")},
            )
            return BorrowResponse(
                success=False,
                message=f"Item is not available (current status: {item.get('current_status')}).",
            )

        owner_id = item.get("owner_id")
        item_name = item.get("name", "Unknown Item")

        # ── Step 2: Database Lock — create PENDING_APPROVAL tx ──────
        tx_data = {
            "item_id": item_id,
            "borrower_id": borrower_id,
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "status": TransactionStatus.PENDING_APPROVAL.value,
        }
        tx_rows = self.supabase_service.create_transaction(tx_data)
        if not tx_rows:
            logger.error("orchestrator.tx_creation_failed", extra={"item_id": item_id})
            return BorrowResponse(
                success=False,
                message="Failed to create transaction. Please try again.",
            )

        transaction_id = tx_rows[0]["id"]
        logger.info(
            "orchestrator.tx_created",
            extra={"transaction_id": transaction_id, "item_id": item_id, "owner_id": owner_id},
        )

        # ── Step 3: Owner Lookup — get their telegram_chat_id ───────
        owner = self.supabase_service.get_user_by_id(owner_id)
        owner_chat_id = owner.get("telegram_chat_id") if owner else None

        if not owner_chat_id:
            # Transaction was created — owner can still approve via portal
            logger.warning(
                "orchestrator.owner_no_telegram",
                extra={"owner_id": owner_id, "transaction_id": transaction_id},
            )
            return BorrowResponse(
                success=True,
                transaction_id=transaction_id,
                message=(
                    f"Request created for {item_name}. "
                    "Owner doesn't have Telegram linked — they'll see it on the portal."
                ),
            )

        # ── Step 4: Push Notification — Telegram approval request ───
        # Look up borrower name for a friendly notification
        borrower = self.supabase_service.get_user_by_id(borrower_id)
        borrower_name = borrower.get("full_name") if borrower else None

        approval_msg = BorrowApprovalMessage(
            transaction_id=transaction_id,
            owner_chat_id=int(owner_chat_id),
            item_name=item_name,
            borrower_name=borrower_name,
            requested_start=payload.requested_start,
            requested_end=payload.requested_end,
        )
        send_result = await self.telegram_service.send_borrow_approval(approval_msg)

        logger.info(
            "orchestrator.telegram_sent",
            extra={
                "transaction_id": transaction_id,
                "owner_chat_id": owner_chat_id,
                "telegram_ok": send_result.ok,
            },
        )

        # ── Step 5: Return success to the Portal ────────────────────
        if send_result.ok:
            return BorrowResponse(
                success=True,
                transaction_id=transaction_id,
                message=f"Request sent! {item_name} owner has been notified on Telegram.",
            )
        else:
            # TX was created, but Telegram push failed — still a partial success
            return BorrowResponse(
                success=True,
                transaction_id=transaction_id,
                message=(
                    f"Request created for {item_name}. "
                    "Telegram notification failed — owner will see it on the portal."
                ),
            )

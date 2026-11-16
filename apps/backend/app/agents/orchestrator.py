"""
NeighbourOrchestrator — Multi-Agent Request and Borrowing Pipeline.

Coordinates:
- Resource validation and atomic state reservation in MongoDB
- Matchmaker discovery (local MongoDB inventory search and ranking)
- Optional Telegram notifications to resource owners
- Calendar invites for handoffs
- Complete fallback when offline or external services are unconfigured
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from app.schemas.api import BorrowRequest, BorrowResponse
from app.schemas.telegram import BorrowApprovalMessage
from app.schemas.transaction import TransactionStatus
from app.services.mongodb_service import MongoDBService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


@dataclass
class NeighbourOrchestrator:
    mongodb_service: MongoDBService
    telegram_service: TelegramService

    async def process_portal_request(self, payload: BorrowRequest) -> BorrowResponse:
        """
        Executes the Borrowing Workflow:
        1. Validates resource exists and is AVAILABLE in MongoDB
        2. Creates a PENDING_APPROVAL borrow request
        3. Pushes an approval notification to the owner (via in-app notification and optional Telegram)
        4. Returns success to the client
        """
        resource_id = payload.item_id
        borrower_id = payload.borrower_id

        # ── Step 1: Fetch resource ──────────────────────────────────
        resource = await self.mongodb_service.get_resource_by_id(resource_id)
        if not resource:
            return BorrowResponse(
                success=False,
                message=f"Resource {resource_id} not found.",
            )

        if resource.get("status") != TransactionStatus.AVAILABLE.value:
            return BorrowResponse(
                success=False,
                message=f"Resource is currently unavailable (status: {resource.get('status')}).",
            )

        owner_id = resource.get("owner_id")
        if str(owner_id) == str(borrower_id):
            return BorrowResponse(
                success=False,
                message="You cannot borrow your own listing.",
            )

        resource_title = resource.get("title", "Item")

        # ── Step 2: Create borrow request with atomic overlap checks
        try:
            borrow_req = await self.mongodb_service.create_borrow_request(
                resource_id=resource_id,
                borrower_id=borrower_id,
                requested_start=payload.requested_start,
                requested_end=payload.requested_end,
                message="Requested via NeighbourNode portal",
            )
        except ValueError as val_err:
            return BorrowResponse(
                success=False,
                message=str(val_err),
            )
        except Exception as e:
            logger.error("Failed to create borrow request: %s", e)
            return BorrowResponse(
                success=False,
                message="Failed to create borrow request. Please try again.",
            )

        request_id = borrow_req["id"]

        # ── Step 3: Owner Lookup & Telegram Push Notification ──────
        owner = await self.mongodb_service.get_user_by_id(owner_id)
        owner_chat_id = owner.get("telegram_chat_id") if owner else None

        if owner_chat_id:
            borrower = await self.mongodb_service.get_user_by_id(borrower_id)
            borrower_name = borrower.get("full_name") if borrower else "A neighbour"

            try:
                approval_msg = BorrowApprovalMessage(
                    transaction_id=request_id,
                    owner_chat_id=int(owner_chat_id),
                    item_name=resource_title,
                    borrower_name=borrower_name,
                    requested_start=payload.requested_start,
                    requested_end=payload.requested_end,
                )
                await self.telegram_service.send_borrow_approval(approval_msg)
            except Exception as e:
                logger.warning("Telegram notification failed (will still appear on portal): %s", e)

        return BorrowResponse(
            success=True,
            transaction_id=request_id,
            message=f"Borrow request sent for '{resource_title}'. Waiting for owner's approval.",
        )

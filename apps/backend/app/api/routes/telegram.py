"""
Telegram webhook route — handles inline button callbacks.

APPROVE flow (the Golden Path closer):
  1. Lookup transaction item_id
  2. approve_transaction() → marks RESERVED in both tables
  3. Build CalendarEventRequest from full transaction data
  4. Create Google Calendar handoff event
  5. Store calendar_event_id on the transaction
  6. Send confirmation message to borrower via Telegram
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import (
    get_calendar_service,
    get_supabase_service,
    get_telegram_service,
)
from app.schemas.api import CalendarEventRequest, WebhookAck
from app.schemas.telegram import TelegramCallbackAction, TelegramCallbackEvent, TelegramSendResult
from app.services.calendar_service import CalendarService
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", response_model=WebhookAck)
async def telegram_webhook(
    request: Request,
    telegram_service: TelegramService = Depends(get_telegram_service),
    calendar_service: CalendarService = Depends(get_calendar_service),
    supabase_service: SupabaseService = Depends(get_supabase_service),
) -> WebhookAck:
    payload: dict[str, Any] = await request.json()
    event = telegram_service.parse_update(payload)
    if not event:
        return WebhookAck(ok=True, detail="ignored")

    await telegram_service.answer_callback(event.callback_id)
    await _handle_callback(event, telegram_service, calendar_service, supabase_service)
    return WebhookAck(ok=True, detail="processed")


async def _handle_callback(
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    calendar_service: CalendarService,
    supabase_service: SupabaseService,
) -> None:
    action = event.payload.action
    tx_id = event.payload.transaction_id

    logger.info(
        "telegram.callback.received",
        extra={
            "action": action,
            "transaction_id": tx_id,
            "user_id": event.user_id,
        },
    )

    if action == TelegramCallbackAction.APPROVE:
        await _handle_approve(tx_id, event, telegram_service, calendar_service, supabase_service)
        return

    if action == TelegramCallbackAction.DECLINE:
        logger.info("telegram.callback.decline.pending", extra={"transaction_id": tx_id})
        return

    if action == TelegramCallbackAction.DONE:
        logger.info("telegram.callback.done.pending", extra={"transaction_id": tx_id})
        return

    if action == TelegramCallbackAction.EXTEND:
        logger.info("telegram.callback.extend.pending", extra={"transaction_id": tx_id})
        return

    if action == TelegramCallbackAction.SUGGEST_TIME:
        logger.info("telegram.callback.suggest_time.pending", extra={"transaction_id": tx_id})
        return


async def _handle_approve(
    transaction_id: str,
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    calendar_service: CalendarService,
    supabase_service: SupabaseService,
) -> None:
    """
    THE GOLDEN PATH CLOSER:
    Approve → RESERVED → Calendar Invite → Notify Borrower.
    """

    # 1. Get item_id from transaction
    item_id = await supabase_service.get_transaction_item_id(transaction_id)
    if not item_id:
        logger.warning(
            "telegram.approve.missing_item",
            extra={"transaction_id": transaction_id},
        )
        return

    # 2. Mark transaction + item as RESERVED
    result = await supabase_service.approve_transaction(transaction_id, item_id)
    if not result.success:
        logger.warning(
            "telegram.approve.update_failed",
            extra={"transaction_id": transaction_id, "message": result.message},
        )
        return

    logger.info(
        "telegram.approve.reserved",
        extra={"transaction_id": transaction_id, "item_id": item_id},
    )

    # 3. Fetch full transaction details for calendar + notification
    tx_full = await supabase_service.get_transaction_full(transaction_id)
    if not tx_full:
        logger.warning("telegram.approve.full_lookup_failed", extra={"transaction_id": transaction_id})
        return

    item_info = tx_full.get("items") or {}
    borrower_info = tx_full.get("borrower") or {}
    owner_info = tx_full.get("owner") or {}
    item_name = item_info.get("name", "Item")
    location = item_info.get("location_hint", "")

    # 4. Create Google Calendar handoff event
    attendee_emails = [
        email for email in [
            borrower_info.get("email"),
            owner_info.get("email"),
        ] if email
    ]

    cal_request = CalendarEventRequest(
        summary=f"NeighbourNode Handoff: {item_name}",
        description=(
            f"Item handoff between {owner_info.get('full_name', 'Owner')} "
            f"and {borrower_info.get('full_name', 'Borrower')}.\n"
            f"Transaction: {transaction_id}"
        ),
        location=location or None,
        start_time=tx_full.get("requested_start"),
        end_time=tx_full.get("requested_end"),
        attendees=attendee_emails,
    )

    cal_result = calendar_service.create_handoff_event(cal_request)
    if cal_result.ok and cal_result.event_id:
        await supabase_service.update_transaction_calendar(
            transaction_id, cal_result.event_id
        )
        logger.info(
            "telegram.approve.calendar_created",
            extra={"transaction_id": transaction_id, "event_id": cal_result.event_id},
        )
    else:
        logger.warning(
            "telegram.approve.calendar_failed",
            extra={"transaction_id": transaction_id, "error": cal_result.error},
        )

    # 5. Send confirmation to borrower via Telegram
    borrower_chat_id = borrower_info.get("telegram_chat_id")
    if borrower_chat_id:
        confirm_text = (
            f"✅ Great news! Your request for **{item_name}** has been approved!\n"
            f"📍 Pickup: {location or 'TBD'}\n"
            f"📅 A calendar invite has been sent."
        )
        await telegram_service._send_message(
            chat_id=int(borrower_chat_id),
            text=confirm_text,
        )
        logger.info(
            "telegram.approve.borrower_notified",
            extra={"transaction_id": transaction_id, "borrower_chat_id": borrower_chat_id},
        )

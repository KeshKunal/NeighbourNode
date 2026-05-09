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
router = APIRouter(prefix="/api/telegram", tags=["telegram"])


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
        await _handle_decline(tx_id, event, telegram_service, supabase_service)
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


from app.schemas.transaction import TransactionStatus

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
    logger.info("telegram.approve.start", extra={"transaction_id": transaction_id})

    # 1. Update DB: Mark transaction as RESERVED
    updated_tx = supabase_service.update_status(transaction_id, TransactionStatus.RESERVED)
    if not updated_tx:
        logger.warning("telegram.approve.update_failed", extra={"transaction_id": transaction_id})
        return

    # 2. Notify Owner: Edit original message to remove buttons and append "✅ Approved!"
    if event.message_id:
        await telegram_service.edit_message(
            chat_id=event.chat_id,
            message_id=event.message_id,
            text=f"✅ Approved!\n\nTransaction ID: {transaction_id}",
            reply_markup=None,  # Removes buttons
        )

    # 3. Notify Borrower
    tx = supabase_service.get_transaction(transaction_id)
    if tx:
        item_id = tx.get("item_id")
        borrower_id = tx.get("borrower_id")

        item = supabase_service.get_item(item_id) if item_id else {}
        item_title = item.get("title", "Unknown Item")  # Strict DB schema uses title

        borrower = supabase_service.get_user_by_id(borrower_id) if borrower_id else {}
        borrower_chat_id = borrower.get("telegram_chat_id")

        if borrower_chat_id:
            confirm_text = f"🎉 Good news! Your request for {item_title} was approved. Please coordinate pickup with the owner."
            await telegram_service._send_message(
                chat_id=int(borrower_chat_id),
                text=confirm_text,
            )
            logger.info("telegram.approve.borrower_notified", extra={"transaction_id": transaction_id})

    # 4. Google Calendar Handoff Event
    if tx:
        # Assuming tx has requested_start and requested_end, or we default them
        from datetime import datetime, timedelta, timezone
        
        # parse iso format from db if available
        start_str = tx.get("requested_start")
        end_str = tx.get("requested_end")
        start_time = datetime.fromisoformat(start_str) if start_str else datetime.now(timezone.utc)
        end_time = datetime.fromisoformat(end_str) if end_str else start_time + timedelta(minutes=30)
        
        # In a real system, you'd pull borrower and owner emails
        owner = supabase_service.get_user_by_id(item.get("owner_id")) if item.get("owner_id") else {}
        attendees = []
        if borrower.get("email"):
            attendees.append(borrower.get("email"))
        if owner.get("email"):
            attendees.append(owner.get("email"))
            
        cal_req = CalendarEventRequest(
            summary=f"NeighbourNode Handoff: {item_title}",
            description=f"Transaction ID: {transaction_id}\nBorrower: {borrower.get('full_name')}\nOwner: {owner.get('full_name')}",
            location=item.get("location_hint") or "Neighbourhood",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            attendees=attendees,
        )
        cal_res = calendar_service.create_handoff_event(cal_req)
        if cal_res.ok:
            logger.info("telegram.approve.calendar_event_created", extra={"event_id": cal_res.event_id})
        else:
            logger.warning("telegram.approve.calendar_event_failed", extra={"error": cal_res.error})

async def _handle_decline(
    transaction_id: str,
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    supabase_service: SupabaseService,
) -> None:
    """
    Decline → CANCELLED → Notify Owner.
    """
    logger.info("telegram.decline.start", extra={"transaction_id": transaction_id})

    # 1. Update DB status to cancelled
    updated_tx = supabase_service.update_status(transaction_id, TransactionStatus.CANCELLED)
    if not updated_tx:
        logger.warning("telegram.decline.update_failed", extra={"transaction_id": transaction_id})
        return

    # 2. Edit the owner's message to show "❌ Declined"
    if event.message_id:
        await telegram_service.edit_message(
            chat_id=event.chat_id,
            message_id=event.message_id,
            text=f"❌ Declined\n\nTransaction ID: {transaction_id}",
            reply_markup=None,
        )



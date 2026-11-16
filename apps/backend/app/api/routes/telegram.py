"""
Telegram webhook route — handles inline button callbacks with MongoDBService.
"""
from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, Depends, Request
from bson import ObjectId

from app.api.dependencies import (
    get_calendar_service,
    get_mongodb_service,
    get_telegram_service,
)
from app.db.mongodb import db, str_to_object_id
from app.schemas.api import CalendarEventRequest, WebhookAck
from app.schemas.telegram import TelegramCallbackAction, TelegramCallbackEvent
from app.schemas.transaction import TransactionStatus
from app.services.calendar_service import CalendarService
from app.services.mongodb_service import MongoDBService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", response_model=WebhookAck)
async def telegram_webhook(
    request: Request,
    telegram_service: TelegramService = Depends(get_telegram_service),
    calendar_service: CalendarService = Depends(get_calendar_service),
    mongodb_service: MongoDBService = Depends(get_mongodb_service),
) -> WebhookAck:
    payload: dict[str, Any] = await request.json()
    event = telegram_service.parse_update(payload)
    if not event:
        return WebhookAck(ok=True, detail="ignored")

    await telegram_service.answer_callback(event.callback_id)
    await _handle_callback(event, telegram_service, calendar_service, mongodb_service)
    return WebhookAck(ok=True, detail="processed")


async def _handle_callback(
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    calendar_service: CalendarService,
    mongodb_service: MongoDBService,
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
        await _handle_approve(tx_id, event, telegram_service, calendar_service, mongodb_service)
        return

    if action == TelegramCallbackAction.DECLINE:
        await _handle_decline(tx_id, event, telegram_service, mongodb_service)
        return


async def _handle_approve(
    transaction_id: str,
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    calendar_service: CalendarService,
    mongodb_service: MongoDBService,
) -> None:
    if db.database is None:
        return

    # Check if this ID is a borrow_request or transaction
    req = await db.database["borrow_requests"].find_one({"_id": str_to_object_id(transaction_id)})
    if req:
        owner_id = str(req["owner_id"])
        await mongodb_service.approve_borrow_request(transaction_id, owner_id)
    else:
        # Fallback for direct tx
        await db.database["transactions"].update_one(
            {"_id": str_to_object_id(transaction_id)},
            {"$set": {"status": TransactionStatus.RESERVED.value}},
        )

    if event.message_id:
        await telegram_service.edit_message(
            chat_id=event.chat_id,
            message_id=event.message_id,
            text=f"✅ Approved! Transaction {transaction_id} is marked RESERVED.",
            reply_markup=None,
        )


async def _handle_decline(
    transaction_id: str,
    event: TelegramCallbackEvent,
    telegram_service: TelegramService,
    mongodb_service: MongoDBService,
) -> None:
    if db.database is None:
        return

    req = await db.database["borrow_requests"].find_one({"_id": str_to_object_id(transaction_id)})
    if req:
        await mongodb_service.reject_borrow_request(transaction_id, str(req["owner_id"]), "Declined via Telegram")

    if event.message_id:
        await telegram_service.edit_message(
            chat_id=event.chat_id,
            message_id=event.message_id,
            text=f"❌ Declined. The borrower has been notified.",
            reply_markup=None,
        )

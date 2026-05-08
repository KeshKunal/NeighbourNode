from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import (
	get_calendar_service,
	get_supabase_service,
	get_telegram_service,
)
from app.schemas.api import WebhookAck
from app.schemas.telegram import TelegramCallbackAction, TelegramCallbackEvent
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
	await _handle_callback(event, calendar_service, supabase_service)
	return WebhookAck(ok=True, detail="processed")


async def _handle_callback(
	event: TelegramCallbackEvent,
	calendar_service: CalendarService,
	supabase_service: SupabaseService,
) -> None:
	logger.info(
		"telegram.callback.received",
		extra={
			"action": event.payload.action,
			"transaction_id": event.payload.transaction_id,
			"user_id": event.user_id,
		},
	)

	if event.payload.action == TelegramCallbackAction.APPROVE:
		item_id = await supabase_service.get_transaction_item_id(
			event.payload.transaction_id
		)
		if not item_id:
			logger.warning(
				"telegram.callback.missing_item",
				extra={"transaction_id": event.payload.transaction_id},
			)
			return

		result = await supabase_service.approve_transaction(
			event.payload.transaction_id,
			item_id,
		)
		if not result.success:
			logger.warning(
				"telegram.callback.update_failed",
				extra={"transaction_id": event.payload.transaction_id},
			)
			return

		# TODO(member3): assemble CalendarEventRequest with real emails + times
		_ = calendar_service
		return

	if event.payload.action == TelegramCallbackAction.DONE:
		logger.info(
			"telegram.callback.done.pending",
			extra={"transaction_id": event.payload.transaction_id},
		)
		return

	if event.payload.action == TelegramCallbackAction.EXTEND:
		logger.info(
			"telegram.callback.extend.pending",
			extra={"transaction_id": event.payload.transaction_id},
		)
		return

	if event.payload.action == TelegramCallbackAction.SUGGEST_TIME:
		logger.info(
			"telegram.callback.suggest_time.pending",
			extra={"transaction_id": event.payload.transaction_id},
		)
		return

	logger.info(
		"telegram.callback.decline.pending",
		extra={"transaction_id": event.payload.transaction_id},
	)

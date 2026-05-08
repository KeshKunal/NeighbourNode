from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
import logging
from typing import Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update

from app.core.config import Settings
from app.schemas.telegram import (
	BorrowApprovalMessage,
	OverdueReminderMessage,
	TelegramCallbackAction,
	TelegramCallbackEvent,
	TelegramCallbackPayload,
	TelegramSendResult,
)


logger = logging.getLogger(__name__)


DEFAULT_PICKUP_SPOT = "Lobby"
LENDER_BATCH_SIZE = 3
TIMEZONE_NAME = "Asia/Kolkata"


@dataclass(frozen=True)
class TelegramService:
	settings: Settings
	_pending_returns: dict[int, "PendingReturnRequest"] | None = None
	_pending_lock: asyncio.Lock | None = None

	def __post_init__(self) -> None:
		if self._pending_returns is None:
			object.__setattr__(self, "_pending_returns", {})
		if self._pending_lock is None:
			object.__setattr__(self, "_pending_lock", asyncio.Lock())

	@property
	def _bot(self) -> Bot | None:
		token = self.settings.telegram_bot_token
		if not token and self.settings.mock_external_services:
			token = "mock-token"
		if not token:
			return None
		return Bot(token=token)

	def _encode_callback(self, action: TelegramCallbackAction, transaction_id: str) -> str:
		return f"{action.value}:{transaction_id}"

	def _decode_callback(self, data: str) -> TelegramCallbackPayload | None:
		try:
			action_raw, transaction_id = data.split(":", 1)
		except ValueError:
			return None
		try:
			action = TelegramCallbackAction(action_raw)
		except ValueError:
			return None
		if not transaction_id:
			return None
		return TelegramCallbackPayload(action=action, transaction_id=transaction_id)

	def _build_approval_keyboard(self, transaction_id: str) -> InlineKeyboardMarkup:
		return InlineKeyboardMarkup(
			[
				[
					InlineKeyboardButton(
						"✅ Approve",
						callback_data=self._encode_callback(
							TelegramCallbackAction.APPROVE, transaction_id
						),
					),
					InlineKeyboardButton(
						"❌ Decline",
						callback_data=self._encode_callback(
							TelegramCallbackAction.DECLINE, transaction_id
						),
					),
				],
				[
					InlineKeyboardButton(
						"⏰ Suggest Time",
						callback_data=self._encode_callback(
							TelegramCallbackAction.SUGGEST_TIME, transaction_id
						),
					)
				],
			]
		)

	def _build_overdue_keyboard(self, transaction_id: str) -> InlineKeyboardMarkup:
		return InlineKeyboardMarkup(
			[
				[
					InlineKeyboardButton(
						"✅ Done",
						callback_data=self._encode_callback(
							TelegramCallbackAction.DONE, transaction_id
						),
					),
					InlineKeyboardButton(
						"⏳ Extend",
						callback_data=self._encode_callback(
							TelegramCallbackAction.EXTEND, transaction_id
						),
					),
				]
			]
		)

	async def send_borrow_approval(self, message: BorrowApprovalMessage) -> TelegramSendResult:
		text = self._format_borrow_request(
			item_name=message.item_name,
			borrower_name=message.borrower_name or "Neighbor",
			requested_start=message.requested_start,
			requested_end=message.requested_end,
			pickup_spot=DEFAULT_PICKUP_SPOT,
		)

		return await self._send_message(
			chat_id=message.owner_chat_id,
			text=text,
			reply_markup=self._build_approval_keyboard(message.transaction_id),
		)

	async def send_lender_batch(
		self,
		notifications: list[BorrowApprovalMessage],
		pickup_spot: str | None = None,
	) -> list[TelegramSendResult]:
		spot = pickup_spot or DEFAULT_PICKUP_SPOT
		results: list[TelegramSendResult] = []
		for message in notifications[:LENDER_BATCH_SIZE]:
			text = self._format_borrow_request(
				item_name=message.item_name,
				borrower_name=message.borrower_name or "Neighbor",
				requested_start=message.requested_start,
				requested_end=message.requested_end,
				pickup_spot=spot,
			)
			results.append(
				await self._send_message(
					chat_id=message.owner_chat_id,
					text=text,
					reply_markup=self._build_approval_keyboard(message.transaction_id),
				)
			)
		return results

	async def send_lender_cancellation(self, chat_id: int) -> TelegramSendResult:
		return await self._send_message(
			chat_id=chat_id,
			text=(
				"Thanks for responding ❤️\n"
				"The borrow request has already been fulfilled by another neighbor."
			),
		)

	async def send_overdue_reminder(self, message: OverdueReminderMessage) -> TelegramSendResult:
		text_lines = [
			"Return reminder:",
			f"Item: {message.item_name}",
			"Your borrowing window has ended.",
			"Reply using the buttons below.",
		]
		return await self._send_message(
			chat_id=message.borrower_chat_id,
			text="\n".join(text_lines),
			reply_markup=self._build_overdue_keyboard(message.transaction_id),
		)

	async def _send_message(
		self,
		chat_id: int,
		text: str,
		reply_markup: InlineKeyboardMarkup | None = None,
	) -> TelegramSendResult:
		if self.settings.mock_external_services:
			logger.info("telegram.send.mock", extra={"chat_id": chat_id, "text": text})
			return TelegramSendResult(ok=True, message_id=None)
		bot = self._bot
		if not bot:
			return TelegramSendResult(ok=False, error="Telegram bot token missing")
		try:
			response = await bot.send_message(
				chat_id=chat_id,
				text=text,
				reply_markup=reply_markup,
			)
			return TelegramSendResult(ok=True, message_id=response.message_id)
		except Exception as exc:  # noqa: BLE001 - surface clean error
			logger.exception("telegram.send.failed")
			return TelegramSendResult(ok=False, error=str(exc))

	async def answer_callback(self, callback_id: str) -> None:
		if self.settings.mock_external_services:
			logger.info("telegram.callback.mock", extra={"callback_id": callback_id})
			return
		bot = self._bot
		if not bot:
			logger.error("telegram.callback.missing_token")
			return
		try:
			await bot.answer_callback_query(callback_id)
		except Exception:
			logger.exception("telegram.callback.failed")

	def parse_update(self, update_payload: dict[str, Any]) -> TelegramCallbackEvent | None:
		bot = self._bot
		if not bot:
			logger.warning("telegram.update.no_bot")
			return None
		update = Update.de_json(update_payload, bot)
		if not update or not update.callback_query or not update.callback_query.data:
			return None
		payload = self._decode_callback(update.callback_query.data)
		if not payload:
			return None
		message = update.callback_query.message
		if not message:
			return None
		return TelegramCallbackEvent(
			payload=payload,
			callback_id=update.callback_query.id,
			chat_id=message.chat.id,
			user_id=update.callback_query.from_user.id,
			message_id=message.message_id,
		)

	def parse_message_update(self, update_payload: dict[str, Any]) -> "TelegramMessageEvent | None":
		bot = self._bot
		if not bot:
			logger.warning("telegram.update.no_bot")
			return None
		update = Update.de_json(update_payload, bot)
		message = update.message if update else None
		if not message or not message.text:
			return None
		return TelegramMessageEvent(
			chat_id=message.chat.id,
			user_id=message.from_user.id,
			text=message.text.strip(),
		)

	async def set_pending_return(self, request: "PendingReturnRequest") -> None:
		if not self._pending_lock or self._pending_returns is None:
			return
		async with self._pending_lock:
			self._pending_returns[request.borrower_chat_id] = request

	async def get_pending_return(self, chat_id: int) -> "PendingReturnRequest | None":
		if not self._pending_lock or self._pending_returns is None:
			return None
		async with self._pending_lock:
			return self._pending_returns.get(chat_id)

	async def clear_pending_return(self, chat_id: int) -> None:
		if not self._pending_lock or self._pending_returns is None:
			return
		async with self._pending_lock:
			self._pending_returns.pop(chat_id, None)

	async def send_text_message(self, chat_id: int, text: str) -> TelegramSendResult:
		return await self._send_message(chat_id=chat_id, text=text)

	async def send_calendar_link(
		self,
		chat_id: int,
		item_name: str,
		borrower_name: str,
		lender_name: str,
		pickup_spot: str,
		return_deadline: str,
		link: str,
	) -> TelegramSendResult:
		text = (
			"Borrow approved.\n"
			f"Item: {item_name}\n"
			f"Borrower: {borrower_name}\n"
			f"Lender: {lender_name}\n"
			f"Pickup: {pickup_spot}\n"
			f"Return by: {return_deadline}\n"
			f"Calendar event: {link}"
		)
		return await self._send_message(chat_id=chat_id, text=text)

	def _format_borrow_request(
		self,
		item_name: str,
		borrower_name: str,
		requested_start: datetime | None,
		requested_end: datetime | None,
		pickup_spot: str,
	) -> str:
		start_text = self._format_datetime(requested_start)
		end_text = self._format_datetime(requested_end)
		return (
			"Your neighbor wants to borrow:\n\n"
			f"🛠 Item: {item_name}\n"
			f"👤 Borrower: {borrower_name}\n"
			f"🕒 Start: {start_text}\n"
			f"↩️ Return By: {end_text}\n"
			f"📍 Pickup: {pickup_spot}\n\n"
			"Reply using the buttons below."
		)

	def _format_datetime(self, value: datetime | None) -> str:
		if not value:
			return "TBD"
			tz = ZoneInfo(TIMEZONE_NAME)
			return value.astimezone(tz).strftime("%Y-%m-%d %I:%M %p %Z")


@dataclass(frozen=True)
class PendingReturnRequest:
	transaction_id: str
	item_id: str
	item_name: str
	borrower_chat_id: int
	lender_chat_id: int
	borrower_name: str
	lender_name: str
	pickup_location: str
	borrow_start: datetime


@dataclass(frozen=True)
class TelegramMessageEvent:
	chat_id: int
	user_id: int
	text: str

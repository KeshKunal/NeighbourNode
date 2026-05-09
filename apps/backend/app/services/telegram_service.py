from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class TelegramService:
	settings: Settings

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
		text_lines = [
			"New borrow request:",
			f"Item: {message.item_name}",
		]
		if message.borrower_name:
			text_lines.append(f"Borrower: {message.borrower_name}")
		if message.requested_start and message.requested_end:
			text_lines.append(
				f"Time: {message.requested_start.isoformat()} - {message.requested_end.isoformat()}"
			)
		text_lines.append("Reply using the buttons below.")
		text = "\n".join(text_lines)

		return await self._send_message(
			chat_id=message.owner_chat_id,
			text=text,
			reply_markup=self._build_approval_keyboard(message.transaction_id),
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

	async def edit_message(
		self,
		chat_id: int,
		message_id: int,
		text: str,
		reply_markup: InlineKeyboardMarkup | None = None,
	) -> TelegramSendResult:
		if self.settings.mock_external_services:
			logger.info("telegram.edit.mock", extra={"chat_id": chat_id, "message_id": message_id, "text": text})
			return TelegramSendResult(ok=True, message_id=message_id)
		bot = self._bot
		if not bot:
			return TelegramSendResult(ok=False, error="Telegram bot token missing")
		try:
			await bot.edit_message_text(
				chat_id=chat_id,
				message_id=message_id,
				text=text,
				reply_markup=reply_markup,
			)
			return TelegramSendResult(ok=True, message_id=message_id)
		except Exception as exc:
			logger.exception("telegram.edit.failed")
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

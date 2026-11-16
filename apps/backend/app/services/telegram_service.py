from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

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

try:
    from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Bot = Any  # type: ignore
    InlineKeyboardButton = Any  # type: ignore
    InlineKeyboardMarkup = Any  # type: ignore
    Update = Any  # type: ignore


@dataclass(frozen=True)
class TelegramService:
    settings: Settings

    @property
    def _bot(self) -> Any | None:
        if not HAS_TELEGRAM:
            return None
        token = self.settings.telegram_bot_token
        if not token and self.settings.mock_external_services:
            token = "mock-token"
        if not token:
            return None
        try:
            return Bot(token=token)
        except Exception:
            return None

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

    def parse_update(self, raw_update: dict[str, Any]) -> TelegramCallbackEvent | None:
        if not HAS_TELEGRAM:
            return None
        try:
            update = Update.de_json(raw_update, self._bot)
        except Exception:
            logger.exception("telegram.update.parse_failed")
            return None

        if not update or not update.callback_query:
            return None

        query = update.callback_query
        data = query.data or ""
        payload = self._decode_callback(data)
        if not payload:
            logger.warning("telegram.callback.unrecognized", extra={"data": data})
            return None

        user = query.from_user
        message = query.message
        return TelegramCallbackEvent(
            callback_id=query.id,
            user_id=user.id if user else 0,
            chat_id=message.chat_id if message else 0,
            message_id=message.message_id if message else None,
            payload=payload,
        )

    async def answer_callback(self, callback_id: str, text: str | None = None) -> None:
        if self.settings.mock_external_services or not HAS_TELEGRAM:
            logger.info("telegram.callback.answered.mock", extra={"callback_id": callback_id})
            return
        bot = self._bot
        if not bot:
            return
        try:
            await bot.answer_callback_query(callback_query_id=callback_id, text=text)
        except Exception:
            logger.exception("telegram.callback.answer_failed")

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Any = None,
    ) -> None:
        if self.settings.mock_external_services or not HAS_TELEGRAM:
            logger.info("telegram.message.edited.mock", extra={"chat_id": chat_id, "message_id": message_id, "text": text})
            return
        bot = self._bot
        if not bot:
            return
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
            )
        except Exception:
            logger.exception("telegram.message.edit_failed")

    async def _send_message(self, chat_id: int, text: str, reply_markup: Any = None) -> TelegramSendResult:
        if self.settings.mock_external_services or not HAS_TELEGRAM:
            logger.info("telegram.send.mock", extra={"chat_id": chat_id, "text": text})
            return TelegramSendResult(ok=True, message_id=12345)
        bot = self._bot
        if not bot:
            return TelegramSendResult(ok=False, error="Telegram bot not configured")
        try:
            msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
            return TelegramSendResult(ok=True, message_id=msg.message_id)
        except Exception as exc:
            logger.exception("telegram.send.failed")
            return TelegramSendResult(ok=False, error=str(exc))

    async def send_borrow_approval(self, message: BorrowApprovalMessage) -> TelegramSendResult:
        reply_markup = None
        if HAS_TELEGRAM:
            approve_btn = InlineKeyboardButton(
                text="✅ Approve",
                callback_data=self._encode_callback(TelegramCallbackAction.APPROVE, message.transaction_id),
            )
            decline_btn = InlineKeyboardButton(
                text="❌ Decline",
                callback_data=self._encode_callback(TelegramCallbackAction.DECLINE, message.transaction_id),
            )
            reply_markup = InlineKeyboardMarkup([[approve_btn, decline_btn]])

        start_str = message.requested_start.strftime("%b %d, %H:%M")
        end_str = message.requested_end.strftime("%b %d, %H:%M")
        text = (
            f"🔔 *New Borrow Request!*\n\n"
            f"*{message.borrower_name or 'A neighbour'}* would like to borrow your *{message.item_name}*.\n\n"
            f"📅 *Duration:* {start_str} → {end_str}\n\n"
            f"Tap below to approve or decline:"
        )
        return await self._send_message(chat_id=message.owner_chat_id, text=text, reply_markup=reply_markup)

    async def send_overdue_reminder(self, message: OverdueReminderMessage) -> TelegramSendResult:
        text = (
            f"⚠️ *Item Return Reminder*\n\n"
            f"Your borrowing window for *{message.item_name}* has ended.\n"
            f"Please return the item to your neighbour or arrange an extension on the portal."
        )
        return await self._send_message(chat_id=message.borrower_chat_id, text=text)

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TelegramCallbackAction(str, Enum):
	APPROVE = "approve"
	DECLINE = "decline"
	SUGGEST_TIME = "suggest_time"
	DONE = "done"
	EXTEND = "extend"


class TelegramCallbackPayload(BaseModel):
	action: TelegramCallbackAction
	transaction_id: str


class TelegramCallbackEvent(BaseModel):
	payload: TelegramCallbackPayload
	callback_id: str
	chat_id: int
	user_id: int
	message_id: int | None = None


class BorrowApprovalMessage(BaseModel):
	transaction_id: str
	owner_chat_id: int
	item_name: str
	borrower_name: str | None = None
	requested_start: datetime | None = None
	requested_end: datetime | None = None


class OverdueReminderMessage(BaseModel):
	transaction_id: str
	borrower_chat_id: int
	item_name: str
	overdue_since: datetime | None = None


class TelegramSendResult(BaseModel):
	ok: bool = True
	message_id: int | None = None
	error: str | None = None

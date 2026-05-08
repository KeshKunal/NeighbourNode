<<<<<<< HEAD
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class BorrowRequest(BaseModel):
    item_id: str
    borrower_id: str
    requested_start: datetime
    requested_end: datetime

class BorrowResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: str

class MatchResult(BaseModel):
    success: bool
    owner_id: Optional[str] = None
    item_id: Optional[str] = None
    proposed_time: Optional[str] = None
    
class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
=======
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OkResponse(BaseModel):
	ok: bool = True


class WebhookAck(OkResponse):
	detail: str | None = None


class CalendarEventRequest(BaseModel):
	summary: str
	start_time: datetime
	end_time: datetime
	timezone: str = "UTC"
	description: str | None = None
	location: str | None = None
	attendees: list[str] = Field(default_factory=list)


class CalendarEventResult(BaseModel):
	ok: bool = True
	event_id: str | None = None
	html_link: str | None = None
	error: str | None = None


class TransactionStatus(str, Enum):
	AVAILABLE = "available"
	PENDING = "pending"
	RESERVED = "reserved"
	OVERDUE = "overdue"
	RETURNED = "returned"


class BorrowRequest(BaseModel):
	item_name: str
	borrower_id: str
	requested_start: datetime
	requested_end: datetime


class MatchResult(BaseModel):
	success: bool
	owner_id: Optional[str] = None
	item_id: Optional[str] = None
	proposed_time: Optional[str] = None
>>>>>>> 9923707 (Implement Telegram integration with calendar and notification services)

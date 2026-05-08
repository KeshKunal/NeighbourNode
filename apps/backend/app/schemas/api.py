"""
API request/response schemas — merged from Member 2 and Member 3.

TransactionStatus is NOT defined here; import from schemas.transaction.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Generic Responses ───────────────────────────────────────────

class OkResponse(BaseModel):
    ok: bool = True


class WebhookAck(OkResponse):
    detail: str | None = None


class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


# ─── Borrow Flow ─────────────────────────────────────────────────

class BorrowRequest(BaseModel):
    """Frontend borrow — caller already knows item_id (from catalog)."""
    item_id: str
    borrower_id: str
    requested_start: datetime
    requested_end: datetime


class BorrowByNameRequest(BaseModel):
    """Agent-driven borrow — user provides a name, Matchmaker finds item."""
    item_name: str
    borrower_id: str
    requested_start: datetime
    requested_end: datetime


class BorrowResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: str


# ─── Agent Results ───────────────────────────────────────────────

class MatchResult(BaseModel):
    success: bool
    owner_id: Optional[str] = None
    item_id: Optional[str] = None
    proposed_time: Optional[str] = None


# ─── Google Calendar ─────────────────────────────────────────────

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

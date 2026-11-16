from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BorrowRequestCreate(BaseModel):
    resource_id: str
    requested_start: datetime
    requested_end: datetime
    message: Optional[str] = "Hi, I would like to borrow this item from you."


class BorrowRequestResponse(BaseModel):
    id: str
    resource_id: str
    resource_title: Optional[str] = None
    borrower_id: str
    borrower_name: Optional[str] = None
    owner_id: str
    owner_name: Optional[str] = None
    requested_start: str
    requested_end: str
    status: str
    message: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    resource_id: str
    resource_title: Optional[str] = None
    borrow_request_id: Optional[str] = None
    borrower_id: str
    borrower_name: Optional[str] = None
    owner_id: str
    owner_name: Optional[str] = None
    approved_start: str
    approved_end: str
    actual_return_date: Optional[str] = None
    status: str
    calendar_event_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


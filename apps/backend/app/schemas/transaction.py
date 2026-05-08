"""
Transaction schemas — THE single source of truth for TransactionStatus.

Every service, agent, and route MUST import TransactionStatus from here.
Values match the Postgres enum in infra/sql/01_initial_schema.sql exactly.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TransactionStatus(str, Enum):
    """Must mirror the 7-value Postgres enum `transaction_status`."""
    AVAILABLE = "available"
    PENDING_APPROVAL = "pending_approval"
    RESERVED = "reserved"
    ACTIVE = "active"
    OVERDUE = "overdue"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class TransactionBase(BaseModel):
    item_id: str
    borrower_id: str
    owner_id: str
    requested_start: datetime
    requested_end: datetime
    status: TransactionStatus = TransactionStatus.PENDING_APPROVAL


class TransactionCreate(TransactionBase):
    pickup_spot: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    approved_start: Optional[datetime] = None
    approved_end: Optional[datetime] = None
    calendar_event_id: Optional[str] = None
    pickup_spot: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdateResult(BaseModel):
    """Returned by SupabaseService after a status mutation."""
    success: bool
    message: str
    transaction_id: Optional[str] = None
    item_id: Optional[str] = None

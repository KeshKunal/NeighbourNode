<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionStatus(str, Enum):
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
    pass

class TransactionResponse(TransactionBase):
    id: str
    approved_start: Optional[datetime] = None
    approved_end: Optional[datetime] = None
    calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
=======
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class TransactionStatus(str, Enum):
	AVAILABLE = "available"
	PENDING = "pending"
	RESERVED = "reserved"
	OVERDUE = "overdue"
	RETURNED = "returned"


class TransactionUpdateResult(BaseModel):
	success: bool
	message: str
	transaction_id: str | None = None
	item_id: str | None = None
>>>>>>> 9923707 (Implement Telegram integration with calendar and notification services)

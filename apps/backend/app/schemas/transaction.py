from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TransactionStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    RETURN_PENDING_CONFIRMATION = "RETURN_PENDING_CONFIRMATION"
    RETURNED = "RETURNED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class TransactionUpdateResult(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[str] = None
    resource_id: Optional[str] = None

"""
Item schemas — uses the canonical TransactionStatus from transaction.py.
Column name is `name` (matches deployed SQL, not the older `title` spec).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .transaction import TransactionStatus


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    current_status: TransactionStatus = TransactionStatus.AVAILABLE


class ItemCreate(ItemBase):
    owner_id: str


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    current_status: Optional[TransactionStatus] = None


class ItemResponse(ItemBase):
    id: str
    owner_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

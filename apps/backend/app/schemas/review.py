from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    reviewed_user_id: str
    transaction_id: Optional[str] = None
    skill_exchange_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=500)


class ReviewResponse(BaseModel):
    id: str
    reviewer_id: str
    reviewer_name: Optional[str] = None
    reviewed_user_id: str
    transaction_id: Optional[str] = None
    skill_exchange_id: Optional[str] = None
    rating: int
    comment: str
    created_at: Optional[str] = None


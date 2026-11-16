from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SkillRequestCreate(BaseModel):
    skill_id: str
    requested_date: datetime
    description: str = Field(..., min_length=5, max_length=500)


class SkillRequestResponse(BaseModel):
    id: str
    skill_id: str
    skill_title: Optional[str] = None
    requester_id: str
    requester_name: Optional[str] = None
    provider_id: str
    provider_name: Optional[str] = None
    requested_date: str
    description: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SkillExchangeResponse(BaseModel):
    id: str
    skill_id: str
    skill_title: Optional[str] = None
    provider_id: str
    provider_name: Optional[str] = None
    requester_id: str
    requester_name: Optional[str] = None
    skill_request_id: Optional[str] = None
    session_date: str
    status: str
    completed_at: Optional[str] = None
    created_at: Optional[str] = None


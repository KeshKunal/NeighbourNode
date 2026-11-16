from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import GeoPoint


class CommunityResponse(BaseModel):
    id: str
    name: str
    description: str
    locality: str
    approximate_location: Optional[GeoPoint] = None
    member_count: int = 0
    created_at: Optional[str] = None


class ConnectionResponse(BaseModel):
    id: str
    requester_id: str
    recipient_id: str
    status: str
    created_at: Optional[str] = None


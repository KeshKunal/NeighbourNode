from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import GeoPoint
from app.schemas.resource import ResourceOwnerSummary


class SkillCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=10, max_length=1000)
    category: str = Field(..., description="Programming | Mathematics tutoring | Graphic design | Music lessons | Photography | Repair assistance | Language learning | Academic guidance | Fitness training | Practical skills")
    experience_level: str = Field("Intermediate", description="Beginner | Intermediate | Expert")
    availability: str = Field("Flexible / Evenings & Weekends")
    location: Optional[GeoPoint] = None
    locality: str = "Mathikere, Bengaluru"
    exchange_type: str = Field("Free / Community Barter", description="Free / Community Barter | Skill Swap | Optional Stipend")


class SkillUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    location: Optional[GeoPoint] = None
    locality: Optional[str] = None
    exchange_type: Optional[str] = None
    status: Optional[str] = None


class SkillResponse(BaseModel):
    id: str
    provider_id: str
    title: str
    description: str
    category: str
    experience_level: str
    availability: str
    location: Optional[GeoPoint] = None
    locality: str
    exchange_type: str
    status: str = "active"
    provider: Optional[ResourceOwnerSummary] = None
    distance_km: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


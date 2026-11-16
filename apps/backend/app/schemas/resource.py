from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import GeoPoint


class ResourceAvailability(BaseModel):
    status: str = "available"
    available_days: List[str] = Field(default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    max_duration_days: int = 7
    notes: Optional[str] = None


class ResourceOwnerSummary(BaseModel):
    id: str
    full_name: str
    locality: str
    reputation_score: float = 4.5
    avatar_url: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=5, max_length=1000)
    category: str = Field(..., description="Electronics | Tools and equipment | Books and study material | Sports equipment | Household items | Kitchen equipment | Travel and camping | Miscellaneous")
    condition: str = Field("Good", description="Like New | Good | Fair")
    images: List[str] = Field(default_factory=list)
    location: Optional[GeoPoint] = None
    locality: str = "Mathikere, Bengaluru"
    availability: Optional[ResourceAvailability] = None
    lending_rules: Optional[str] = "Please handle with care and return on time."


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    images: Optional[List[str]] = None
    location: Optional[GeoPoint] = None
    locality: Optional[str] = None
    availability: Optional[ResourceAvailability] = None
    lending_rules: Optional[str] = None
    status: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    description: str
    category: str
    condition: str
    images: List[str] = Field(default_factory=list)
    location: Optional[GeoPoint] = None
    locality: str
    availability: Optional[ResourceAvailability] = None
    lending_rules: Optional[str] = None
    status: str = "AVAILABLE"
    owner: Optional[ResourceOwnerSummary] = None
    distance_km: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


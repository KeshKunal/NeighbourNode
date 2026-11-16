from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import GeoPoint


class ReputationBreakdown(BaseModel):
    score: float = Field(..., ge=1.0, le=5.0)
    average_rating: float = 0.0
    review_count: int = 0
    completed_exchanges: int = 0
    on_time_return_rate: float = 1.0
    verified_bonus: float = 0.0
    explanation: str = "Based on completed exchanges, community reviews, and on-time returns."


class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.\+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    locality: str = Field("Mathikere, Bengaluru", description="Neighbourhood or locality name")
    building: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[GeoPoint] = None
    location_visibility: str = Field("approximate", description="approximate | exact | hidden")
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    avatar_url: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    locality: Optional[str] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[GeoPoint] = None
    location_visibility: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    telegram_chat_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    locality: str = "Mathikere, Bengaluru"
    community_id: Optional[str] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[GeoPoint] = None
    location_visibility: str = "approximate"
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    reputation_score: float = 4.5
    reputation_breakdown: Optional[ReputationBreakdown] = None
    completed_exchanges: int = 0
    is_verified: bool = True
    is_active: bool = True
    telegram_chat_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserPublicProfile(BaseModel):
    id: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    locality: str
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    reputation_score: float
    completed_exchanges: int
    is_verified: bool
    distance_km: Optional[float] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

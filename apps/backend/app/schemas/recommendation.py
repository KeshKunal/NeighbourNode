from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.resource import ResourceResponse
from app.schemas.skill import SkillResponse
from app.schemas.users import UserPublicProfile


class RecommendationFactorBreakdown(BaseModel):
    relevance: float
    proximity: float
    availability: float
    reputation: float
    community_relationship: float
    previous_interaction: float
    total_score: float
    explanation: str


class ResourceRecommendation(BaseModel):
    resource: ResourceResponse
    score: float
    breakdown: RecommendationFactorBreakdown


class SkillRecommendation(BaseModel):
    skill: SkillResponse
    score: float
    breakdown: RecommendationFactorBreakdown


class NeighbourRecommendation(BaseModel):
    neighbour: UserPublicProfile
    score: float
    shared_interests: List[str]
    breakdown: RecommendationFactorBreakdown


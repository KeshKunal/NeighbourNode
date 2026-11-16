"""
Recommendations routes for NeighbourNode (/api/v1/recommendations).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_mongodb_service, get_optional_current_user
from app.schemas.recommendation import (
    NeighbourRecommendation,
    ResourceRecommendation,
    SkillRecommendation,
)
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/resources", response_model=List[ResourceRecommendation])
async def get_resource_recommendations(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[ResourceRecommendation]:
    user_id = current_user["id"] if current_user else None
    coords = None
    if current_user and current_user.get("location"):
        coords = current_user["location"].get("coordinates")
    else:
        coords = [77.5649, 13.0308]  # Bengaluru default

    recs = await mongodb_svc.get_recommended_resources(
        user_id=user_id,
        query=query,
        category=category,
        user_coordinates=coords,
        limit=limit,
    )
    return [ResourceRecommendation(**r) for r in recs]


@router.get("/skills", response_model=List[SkillRecommendation])
async def get_skill_recommendations(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[SkillRecommendation]:
    user_id = current_user["id"] if current_user else None
    coords = None
    if current_user and current_user.get("location"):
        coords = current_user["location"].get("coordinates")
    else:
        coords = [77.5649, 13.0308]

    recs = await mongodb_svc.get_recommended_skills(
        user_id=user_id,
        query=query,
        category=category,
        user_coordinates=coords,
        limit=limit,
    )
    return [SkillRecommendation(**r) for r in recs]


@router.get("/neighbours", response_model=List[NeighbourRecommendation])
async def get_neighbour_recommendations(
    limit: int = Query(10, ge=1, le=20),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[NeighbourRecommendation]:
    user_id = current_user["id"] if current_user else "000000000000000000000000"
    recs = await mongodb_svc.get_recommended_neighbours(user_id=user_id, limit=limit)
    return [NeighbourRecommendation(**r) for r in recs]


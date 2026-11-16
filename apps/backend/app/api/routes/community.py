"""
Community Directory and Discovery routes for NeighbourNode (/api/v1/community).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user, get_mongodb_service, get_optional_current_user
from app.schemas.community import CommunityResponse
from app.schemas.recommendation import NeighbourRecommendation
from app.schemas.users import UserPublicProfile
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/community", tags=["community"])


@router.get("", response_model=List[UserPublicProfile])
@router.get("/", response_model=List[UserPublicProfile], include_in_schema=False)
async def list_community_members(
    locality: Optional[str] = Query(None),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[UserPublicProfile]:
    members = await mongodb_svc.list_community_members(locality=locality)
    return [
        UserPublicProfile(
            id=m["id"],
            full_name=m["full_name"],
            avatar_url=m.get("avatar_url"),
            bio=m.get("bio"),
            locality=m.get("locality", "Bengaluru"),
            skills=m.get("skills", []),
            interests=m.get("interests", []),
            reputation_score=m.get("reputation_score", 4.5),
            completed_exchanges=m.get("completed_exchanges", 0),
            is_verified=m.get("is_verified", True),
        )
        for m in members
    ]


@router.get("/groups", response_model=List[CommunityResponse])
async def list_community_groups(
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[CommunityResponse]:
    groups = await mongodb_svc.list_communities()
    return [CommunityResponse(**g) for g in groups]


@router.get("/recommendations", response_model=List[NeighbourRecommendation])
async def get_neighbour_recommendations(
    limit: int = Query(10, ge=1, le=20),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[NeighbourRecommendation]:
    user_id = current_user["id"] if current_user else "000000000000000000000000"
    recs = await mongodb_svc.get_recommended_neighbours(user_id=user_id, limit=limit)
    return [NeighbourRecommendation(**r) for r in recs]


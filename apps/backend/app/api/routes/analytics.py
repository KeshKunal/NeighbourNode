"""
Analytics routes for NeighbourNode (/api/v1/analytics).
Directly executes MongoDB Aggregation Pipelines (Section 9.B).
"""
from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_mongodb_service
from app.schemas.analytics import CommunityAnalyticsResponse, UserAnalyticsResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/community", response_model=CommunityAnalyticsResponse)
async def get_community_analytics(
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> CommunityAnalyticsResponse:
    data = await mongodb_svc.get_community_analytics()
    return CommunityAnalyticsResponse(**data)


@router.get("/me", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> UserAnalyticsResponse:
    data = await mongodb_svc.get_user_analytics(user_id=current_user["id"])
    return UserAnalyticsResponse(**data)


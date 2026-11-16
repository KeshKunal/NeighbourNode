"""
Users routes for NeighbourNode (/api/v1/users).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_mongodb_service
from app.schemas.review import ReviewResponse
from app.schemas.users import UserProfileUpdate, UserPublicProfile, UserResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> UserResponse:
    user = await mongodb_svc.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    payload: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> UserResponse:
    update_data = payload.model_dump(exclude_unset=True)
    updated = await mongodb_svc.update_user(current_user["id"], update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update profile")
    return UserResponse(**updated)


@router.get("/{user_id}", response_model=UserPublicProfile)
async def get_public_user_profile(
    user_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> UserPublicProfile:
    user = await mongodb_svc.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublicProfile(
        id=user["id"],
        full_name=user["full_name"],
        avatar_url=user.get("avatar_url"),
        bio=user.get("bio"),
        locality=user.get("locality", "Bengaluru"),
        skills=user.get("skills", []),
        interests=user.get("interests", []),
        reputation_score=user.get("reputation_score", 4.5),
        completed_exchanges=user.get("completed_exchanges", 0),
        is_verified=user.get("is_verified", True),
    )


@router.get("/{user_id}/reviews", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[ReviewResponse]:
    reviews = await mongodb_svc.list_user_reviews(user_id)
    return [ReviewResponse(**r) for r in reviews]


# Backwards compatibility endpoints
@router.put("/profile", response_model=UserResponse)
async def legacy_update_profile(
    payload: Dict[str, Any],
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> UserResponse:
    user_id = payload.get("user_id") or payload.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    updated = await mongodb_svc.update_user(user_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**updated)

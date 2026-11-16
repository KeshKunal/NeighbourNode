"""
Reviews routes for NeighbourNode (/api/v1/reviews).
"""
from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.api.dependencies import get_current_user, get_mongodb_service
from app.db.mongodb import db, serialize_doc, str_to_object_id
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_review(
    payload: ReviewCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ReviewResponse:
    try:
        review = await mongodb_svc.create_review(
            reviewer_id=current_user["id"],
            reviewed_user_id=payload.reviewed_user_id,
            rating=payload.rating,
            comment=payload.comment,
            transaction_id=payload.transaction_id,
            skill_exchange_id=payload.skill_exchange_id,
        )
        return ReviewResponse(**review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create review: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ReviewResponse:
    if db.database is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    doc = await db.database["reviews"].find_one({"_id": str_to_object_id(review_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Review not found")
    serialized = serialize_doc(doc)
    reviewer = await mongodb_svc.get_user_by_id(doc["reviewer_id"])
    if reviewer:
        serialized["reviewer_name"] = reviewer.get("full_name")
    return ReviewResponse(**serialized)


"""
Skill Requests and Exchange routes for NeighbourNode (/api/v1/skill-requests).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_mongodb_service
from app.schemas.skill_exchange import SkillRequestCreate, SkillRequestResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skill-requests", tags=["skill-exchanges"])


@router.post("", response_model=SkillRequestResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=SkillRequestResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_skill_request(
    payload: SkillRequestCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> SkillRequestResponse:
    try:
        req = await mongodb_svc.create_skill_request(
            skill_id=payload.skill_id,
            requester_id=current_user["id"],
            requested_date=payload.requested_date,
            description=payload.description,
        )
        return SkillRequestResponse(**req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create skill request: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[SkillRequestResponse])
@router.get("/", response_model=List[SkillRequestResponse], include_in_schema=False)
async def list_skill_requests(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[SkillRequestResponse]:
    requests = await mongodb_svc.list_skill_requests(user_id=current_user["id"])
    return [SkillRequestResponse(**r) for r in requests]


@router.post("/{request_id}/accept")
async def accept_skill_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    success = await mongodb_svc.accept_skill_request(request_id=request_id, provider_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Unable to accept skill request")
    return {"message": "Skill session accepted and scheduled"}


@router.post("/{request_id}/complete")
async def complete_skill_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    success = await mongodb_svc.complete_skill_exchange(request_id=request_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Unable to mark skill exchange complete")
    return {"message": "Skill session marked completed. You can now leave a review."}


"""
Skills routes for NeighbourNode (/api/v1/skills).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_mongodb_service
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=List[SkillResponse])
@router.get("/", response_model=List[SkillResponse], include_in_schema=False)
async def list_skills(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    provider_id: Optional[str] = Query(None),
    locality: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[SkillResponse]:
    skills = await mongodb_svc.list_skills(
        category=category,
        search=search,
        provider_id=provider_id,
        locality=locality,
        limit=limit,
        skip=skip,
    )
    return [SkillResponse(**s) for s in skills]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> SkillResponse:
    skill = await mongodb_svc.get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill listing not found")
    return SkillResponse(**skill)


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_skill(
    payload: SkillCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> SkillResponse:
    data = payload.model_dump()
    data["provider_id"] = current_user["id"]
    if not data.get("location") and current_user.get("location"):
        data["location"] = current_user["location"]
    elif not data.get("location"):
        data["location"] = {"type": "Point", "coordinates": [77.5649, 13.0308]}

    created = await mongodb_svc.create_skill(data)
    return SkillResponse(**created)


@router.patch("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    payload: SkillUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> SkillResponse:
    update_data = payload.model_dump(exclude_unset=True)
    updated = await mongodb_svc.update_skill(
        skill_id=skill_id,
        update_fields=update_data,
        provider_id=current_user["id"],
    )
    if not updated:
        raise HTTPException(status_code=403, detail="Skill not found or you are not the provider")
    return SkillResponse(**updated)


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    deleted = await mongodb_svc.delete_skill(skill_id=skill_id, provider_id=current_user["id"])
    if not deleted:
        raise HTTPException(status_code=403, detail="Skill not found or you are not the provider")
    return {"message": "Skill deleted successfully"}


"""
Resources routes for NeighbourNode (/api/v1/resources).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_mongodb_service, get_optional_current_user
from app.schemas.resource import ResourceCreate, ResourceResponse, ResourceUpdate
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=List[ResourceResponse])
@router.get("/", response_model=List[ResourceResponse], include_in_schema=False)
async def list_resources(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    locality: Optional[str] = Query(None),
    owner_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[ResourceResponse]:
    items = await mongodb_svc.list_resources(
        category=category,
        status=status,
        search=search,
        locality=locality,
        owner_id=owner_id,
        limit=limit,
        skip=skip,
    )
    return [ResourceResponse(**i) for i in items]


@router.get("/nearby", response_model=List[ResourceResponse])
async def get_nearby_resources(
    longitude: float = Query(77.5649, description="Longitude in Bengaluru"),
    latitude: float = Query(13.0308, description="Latitude in Bengaluru"),
    max_distance_meters: float = Query(10000.0, ge=100.0, le=50000.0),
    category: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=50),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[ResourceResponse]:
    items = await mongodb_svc.find_nearby_resources(
        longitude=longitude,
        latitude=latitude,
        max_distance_meters=max_distance_meters,
        category=category,
        limit=limit,
    )
    return [ResourceResponse(**i) for i in items]


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ResourceResponse:
    item = await mongodb_svc.get_resource_by_id(resource_id)
    if not item:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse(**item)


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_resource(
    payload: ResourceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ResourceResponse:
    data = payload.model_dump()
    data["owner_id"] = current_user["id"]

    # Inherit location from user profile if not explicitly provided
    if not data.get("location") and current_user.get("location"):
        data["location"] = current_user["location"]
    elif not data.get("location"):
        # Default Bengaluru MSRIT coordinates
        data["location"] = {"type": "Point", "coordinates": [77.5649, 13.0308]}

    created = await mongodb_svc.create_resource(data)
    return ResourceResponse(**created)


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    payload: ResourceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ResourceResponse:
    update_data = payload.model_dump(exclude_unset=True)
    updated = await mongodb_svc.update_resource(
        resource_id=resource_id,
        update_fields=update_data,
        owner_id=current_user["id"],
    )
    if not updated:
        raise HTTPException(status_code=403, detail="Resource not found or you are not the owner")
    return ResourceResponse(**updated)


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    deleted = await mongodb_svc.delete_resource(resource_id=resource_id, owner_id=current_user["id"])
    if not deleted:
        raise HTTPException(status_code=403, detail="Resource not found or you are not the owner")
    return {"message": "Resource deleted successfully"}


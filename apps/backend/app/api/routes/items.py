"""
Items route — backwards compatible alias for /resources.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_mongodb_service, get_optional_current_user
from app.schemas.resource import ResourceCreate, ResourceResponse, ResourceUpdate
from app.services.mongodb_service import MongoDBService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ResourceResponse])
async def list_items(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[ResourceResponse]:
    items = await mongodb_svc.list_resources(status=status, category=category, search=search)
    return [ResourceResponse(**i) for i in items]


@router.post("/", response_model=ResourceResponse)
async def create_item(
    payload: ResourceCreate,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ResourceResponse:
    data = payload.model_dump()
    owner_id = current_user["id"] if current_user else "666666666666666666666666"
    data["owner_id"] = owner_id
    if not data.get("location"):
        data["location"] = {"type": "Point", "coordinates": [77.5649, 13.0308]}
    created = await mongodb_svc.create_resource(data)
    return ResourceResponse(**created)


@router.get("/{item_id}", response_model=ResourceResponse)
async def get_item(
    item_id: str,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> ResourceResponse:
    item = await mongodb_svc.get_resource_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ResourceResponse(**item)

"""
Notifications routes for NeighbourNode (/api/v1/notifications).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, get_mongodb_service
from app.schemas.notification import NotificationResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse], include_in_schema=False)
async def list_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[NotificationResponse]:
    notes = await mongodb_svc.list_notifications(user_id=current_user["id"])
    return [NotificationResponse(**n) for n in notes]


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, bool]:
    success = await mongodb_svc.mark_notification_read(notification_id=notification_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"ok": True}


@router.post("/read-all")
async def mark_all_read(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, int]:
    count = await mongodb_svc.mark_all_notifications_read(user_id=current_user["id"])
    return {"marked_read": count}


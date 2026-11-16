from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    related_entity_id: Optional[str] = None
    is_read: bool = False
    created_at: Optional[str] = None


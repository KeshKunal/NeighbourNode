"""
FastAPI dependency factories for NeighbourNode.
Provides MongoDBService, TelegramService, CalendarService, NotificationService singletons.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import get_settings
from app.core.security import get_current_user, get_optional_current_user
from app.services.calendar_service import CalendarService
from app.services.mongodb_service import MongoDBService
from app.services.notification_service import NotificationService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


@lru_cache
def get_mongodb_service() -> MongoDBService:
    return MongoDBService()


@lru_cache
def get_telegram_service() -> TelegramService:
    return TelegramService(get_settings())


@lru_cache
def get_calendar_service() -> CalendarService:
    return CalendarService(get_settings())


@lru_cache
def get_notification_service() -> NotificationService:
    return NotificationService(get_settings())

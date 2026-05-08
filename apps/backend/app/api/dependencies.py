"""
FastAPI dependency factories — merged from Member 2 and Member 3.

Single source of service singletons for dependency injection.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from app.core.config import get_settings
from app.services.calendar_service import CalendarService
from app.services.notification_service import NotificationService
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)


@lru_cache
def get_telegram_service() -> TelegramService:
    return TelegramService(get_settings())


@lru_cache
def get_calendar_service() -> CalendarService:
    return CalendarService(get_settings())


@lru_cache
def get_notification_service() -> NotificationService:
    return NotificationService(get_settings())


@lru_cache
def get_supabase_service() -> SupabaseService:
    """
    Build a SupabaseService with a real client when credentials are
    available, otherwise fall back to a client-less instance (safe for
    mock / offline testing).
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if url and key:
        try:
            from supabase import create_client
            client = create_client(url, key)
            logger.info("supabase.client.connected", extra={"url": url})
            return SupabaseService(db_client=client)
        except Exception:
            logger.exception("supabase.client.creation.failed")

    logger.warning("supabase.client.no_credentials — running without DB")
    return SupabaseService(db_client=None)

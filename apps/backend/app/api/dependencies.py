import os
from supabase import create_client, Client
from app.services.supabase_service import SupabaseService
from fastapi import Request

# Usually fetched from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://localhost:8000") # placeholder
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "placeholder_key")

# We can cache the client
_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_supabase_service() -> SupabaseService:
    client = get_supabase_client()
    return SupabaseService(client)
from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.calendar_service import CalendarService
from app.services.notification_service import NotificationService
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService


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
	return SupabaseService()

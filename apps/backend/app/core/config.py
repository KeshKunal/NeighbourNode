from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import os
from typing import Any


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    return value.strip()


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # MongoDB
    mongodb_uri: str
    mongodb_database: str

    # Security & JWT
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int

    # Frontend
    frontend_url: str

    # Optional Telegram Bot
    telegram_bot_token: str | None
    telegram_webhook_secret: str | None

    # Optional Google Calendar
    google_calendar_id: str | None
    google_credentials_json: dict[str, Any] | None
    google_credentials_path: str | None

    # Optional Cloudinary / Image storage
    image_storage_cloud_name: str | None
    image_storage_api_key: str | None
    image_storage_api_secret: str | None

    # Optional AI / Gemini
    ai_api_base_url: str | None
    ai_api_key: str | None
    ai_model: str

    mock_external_services: bool


@lru_cache
def get_settings() -> Settings:
    raw_json = _get_env("GOOGLE_CREDENTIALS_JSON")
    credentials_json = json.loads(raw_json) if raw_json else None

    # Default MongoDB to local or Atlas connection string
    mongodb_uri = _get_env("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database = _get_env("MONGODB_DATABASE", "neighbournode")

    return Settings(
        mongodb_uri=mongodb_uri or "mongodb://localhost:27017",
        mongodb_database=mongodb_database or "neighbournode",
        jwt_secret_key=_get_env("JWT_SECRET_KEY", "dev-secret-key-csaec59-neighbournode-2026"),
        jwt_algorithm=_get_env("JWT_ALGORITHM", "HS256") or "HS256",
        access_token_expire_minutes=_get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 1440),
        frontend_url=_get_env("FRONTEND_URL", "http://localhost:3000") or "http://localhost:3000",
        telegram_bot_token=_get_env("TELEGRAM_BOT_TOKEN"),
        telegram_webhook_secret=_get_env("TELEGRAM_WEBHOOK_SECRET"),
        google_calendar_id=_get_env("GOOGLE_CALENDAR_ID"),
        google_credentials_json=credentials_json,
        google_credentials_path=_get_env("GOOGLE_CREDENTIALS_PATH"),
        image_storage_cloud_name=_get_env("IMAGE_STORAGE_CLOUD_NAME"),
        image_storage_api_key=_get_env("IMAGE_STORAGE_API_KEY"),
        image_storage_api_secret=_get_env("IMAGE_STORAGE_API_SECRET"),
        ai_api_base_url=_get_env("AI_API_BASE_URL"),
        ai_api_key=_get_env("AI_API_KEY"),
        ai_model=_get_env("AI_MODEL", "gemini-1.5-flash"),
        mock_external_services=_get_bool("MOCK_EXTERNAL_SERVICES", default=True),
    )

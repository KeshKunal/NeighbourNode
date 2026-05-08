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


@dataclass(frozen=True)
class Settings:
	telegram_bot_token: str | None
	telegram_webhook_secret: str | None
	google_calendar_id: str | None
	google_credentials_json: dict[str, Any] | None
	google_credentials_path: str | None
	mock_external_services: bool


@lru_cache
def get_settings() -> Settings:
	raw_json = _get_env("GOOGLE_CREDENTIALS_JSON")
	credentials_json = json.loads(raw_json) if raw_json else None
	return Settings(
		telegram_bot_token=_get_env("TELEGRAM_BOT_TOKEN"),
		telegram_webhook_secret=_get_env("TELEGRAM_WEBHOOK_SECRET"),
		google_calendar_id=_get_env("GOOGLE_CALENDAR_ID"),
		google_credentials_json=credentials_json,
		google_credentials_path=_get_env("GOOGLE_CREDENTIALS_PATH"),
		mock_external_services=_get_bool("MOCK_EXTERNAL_SERVICES", default=False),
	)

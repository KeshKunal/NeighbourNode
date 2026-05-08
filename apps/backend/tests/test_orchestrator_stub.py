from __future__ import annotations

import pytest

from app.agents.orchestrator import run_orchestrator
from app.agents.state import OrchestrationState
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService
from app.core.config import Settings


def _mock_settings() -> Settings:
    return Settings(
        telegram_bot_token=None,
        telegram_webhook_secret=None,
        google_calendar_id=None,
        google_credentials_json=None,
        google_credentials_path=None,
        mock_external_services=True,
    )


@pytest.mark.asyncio
async def test_orchestrator_runs_scavenger_on_miss() -> None:
    """When Matchmaker finds no match, orchestrator should fall through to Scavenger."""
    state: OrchestrationState = {
        "user_id": "demo-user",
        "item_name": "unicorn saddle",  # guaranteed not in any DB
        "requested_start": "2026-05-08T10:00:00Z",
        "requested_end": "2026-05-08T14:00:00Z",
        "status": "new",
        "errors": [],
    }
    supabase_svc = SupabaseService(db_client=None)
    telegram_svc = TelegramService(_mock_settings())

    result = await run_orchestrator(state, supabase_svc, telegram_svc)
    assert "match_result" in result
    assert "scavenger_results" in result
from __future__ import annotations

import pytest

from app.agents.orchestrator import NeighbourOrchestrator
from app.schemas.api import BorrowRequest
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService
from app.core.config import Settings
from datetime import datetime, timezone


def _mock_settings() -> Settings:
    return Settings(
        telegram_bot_token=None,
        telegram_webhook_secret=None,
        google_calendar_id=None,
        google_credentials_json=None,
        google_credentials_path=None,
        mock_external_services=True,
        ai_api_base_url=None,
        ai_api_key=None,
        ai_model="test",
    )


@pytest.mark.asyncio
async def test_orchestrator_item_not_found() -> None:
    """When item doesn't exist, orchestrator should return failure."""
    supabase_svc = SupabaseService(db_client=None)
    telegram_svc = TelegramService(_mock_settings())

    orchestrator = NeighbourOrchestrator(
        supabase_service=supabase_svc,
        telegram_service=telegram_svc,
    )

    payload = BorrowRequest(
        item_id="nonexistent-item",
        borrower_id="demo-user",
        requested_start=datetime.now(timezone.utc),
        requested_end=datetime.now(timezone.utc),
    )

    result = await orchestrator.process_portal_request(payload)
    assert result.success is False
    assert "not found" in result.message.lower()
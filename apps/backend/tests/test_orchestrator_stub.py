from __future__ import annotations

import pytest

from app.agents.adk_runtime import AdkRunRequest
from app.agents.orchestrator import run_orchestrator_with_adk
from app.agents.state import OrchestrationState


class StubRuntime:
    async def run(self, request: AdkRunRequest) -> dict[str, object]:
        if request.agent_name == "matchmaker":
            return {
                "success": False,
                "owner_id": None,
                "item_id": None,
                "proposed_time": None,
                "reason": "stub",
            }
        if request.agent_name == "scavenger":
            return {"results": []}
        return {}


@pytest.mark.asyncio
async def test_orchestrator_runs_scavenger_on_miss() -> None:
    state: OrchestrationState = {
        "user_id": "demo-user",
        "item_name": "power drill",
        "requested_start": "2026-05-08T10:00:00Z",
        "requested_end": "2026-05-08T14:00:00Z",
        "status": "pending_approval",
        "errors": [],
    }
    result = await run_orchestrator_with_adk(state, StubRuntime())
    assert "match_result" in result
    assert "scavenger_results" in result
*** End Patch
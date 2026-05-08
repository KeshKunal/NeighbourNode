from __future__ import annotations

import asyncio

from .adk_runtime import AdkRunRequest
from .orchestrator import run_orchestrator_with_adk
from .state import OrchestrationState


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


async def _main() -> None:
    state: OrchestrationState = {
        "user_id": "demo-user",
        "item_name": "power drill",
        "requested_start": "2026-05-08T10:00:00Z",
        "requested_end": "2026-05-08T14:00:00Z",
        "status": "pending_approval",
        "errors": [],
    }
    result = await run_orchestrator_with_adk(state, StubRuntime())
    print(result)


if __name__ == "__main__":
    asyncio.run(_main())

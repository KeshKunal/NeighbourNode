from __future__ import annotations

from typing import Any

from .adk_runtime import AdkRunRequest
from .matchmaker.agent import run_matchmaker
from .scavenger.agent import run_scavenger


class AdkGoogleRuntime:
    async def run(self, request: AdkRunRequest) -> dict[str, Any]:
        if request.agent_name == "matchmaker":
            return await run_matchmaker(request.state)
        if request.agent_name == "scavenger":
            return await run_scavenger(request.state)
        return {"success": False, "reason": "unknown_agent"}

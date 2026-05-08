from __future__ import annotations

from ..state import MatchmakerResult, OrchestrationState


async def run_matchmaker(state: OrchestrationState) -> MatchmakerResult:
    return {
        "success": False,
        "owner_id": None,
        "item_id": None,
        "proposed_time": None,
        "reason": "not_implemented",
    }

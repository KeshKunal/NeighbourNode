from __future__ import annotations

from ..state import OrchestrationState, ScavengerResult


async def run_scavenger(state: OrchestrationState) -> ScavengerResult:
    return {"results": []}

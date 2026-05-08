from __future__ import annotations

from .adk_runtime import AdkRuntime, AdkRunRequest
from .state import OrchestrationState, MatchmakerResult, ScavengerResult
from .matchmaker.agent import run_matchmaker
from .scavenger.agent import run_scavenger


async def run_orchestrator(state: OrchestrationState) -> OrchestrationState:
    match_result: MatchmakerResult = await run_matchmaker(state)
    state["match_result"] = match_result

    if match_result.get("success"):
        return state

    scavenger_result: ScavengerResult = await run_scavenger(state)
    state["scavenger_results"] = scavenger_result.get("results", [])
    return state


async def run_orchestrator_with_adk(
	state: OrchestrationState,
	runtime: AdkRuntime,
) -> OrchestrationState:
	match_request = AdkRunRequest(agent_name="matchmaker", state=state)
	match_result = await runtime.run(match_request)
	state["match_result"] = match_result

	if match_result.get("success"):
		return state

	scavenger_request = AdkRunRequest(agent_name="scavenger", state=state)
	scavenger_result = await runtime.run(scavenger_request)
	state["scavenger_results"] = scavenger_result.get("results", [])
	return state

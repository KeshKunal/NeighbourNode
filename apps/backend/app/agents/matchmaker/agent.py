from __future__ import annotations

import json
import os
from pathlib import Path

from google.adk import Agent

from ..state import MatchmakerResult, OrchestrationState


def search_local_inventory(item_name: str) -> dict[str, str]:
    if "drill" in item_name.lower():
        return {
            "status": "found",
            "owner_id": "user_42",
            "item_id": "item_1001",
            "item_name": "Bosch Power Drill",
        }
    return {"status": "not_found"}


def _load_prompt() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    prompt_path = repo_root / "packages" / "prompts" / "matchmaker_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


def _build_matchmaker_agent() -> Agent:
    instruction = _load_prompt()
    model = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")
    return Agent(
        name="MatchmakerBroker",
        model=model,
        instruction=instruction,
        tools=[search_local_inventory],
    )


def _parse_matchmaker_response(text: str) -> MatchmakerResult:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            "success": False,
            "owner_id": None,
            "item_id": None,
            "proposed_time": None,
            "reason": "invalid_json",
        }

    return {
        "success": bool(payload.get("success")),
        "owner_id": payload.get("owner_id"),
        "item_id": payload.get("item_id"),
        "proposed_time": payload.get("proposed_time"),
        "reason": payload.get("reason"),
    }


async def run_matchmaker(state: OrchestrationState) -> MatchmakerResult:
    agent = _build_matchmaker_agent()
    prompt = (
        "User request for local matching.\n"
        f"item_name: {state['item_name']}\n"
        f"requested_start: {state['requested_start']}\n"
        f"requested_end: {state['requested_end']}\n"
        f"user_id: {state['user_id']}"
    )
    response = agent.run(prompt)
    return _parse_matchmaker_response(response.text)

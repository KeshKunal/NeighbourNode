from __future__ import annotations

import json
import os
from pathlib import Path

from google.adk import Agent
from google.adk.tools import google_search

from ..state import OrchestrationState, ScavengerResult


def _load_prompt() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    prompt_path = repo_root / "packages" / "prompts" / "scavenger_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


def _build_scavenger_agent() -> Agent:
    instruction = _load_prompt()
    model = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro-latest")
    return Agent(
        name="LocalScavenger",
        model=model,
        instruction=instruction,
        tools=[google_search],
    )


def _parse_scavenger_response(text: str) -> ScavengerResult:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"results": []}

    results = payload.get("results") or []
    return {"results": list(results)}


async def run_scavenger(state: OrchestrationState) -> ScavengerResult:
    agent = _build_scavenger_agent()
    prompt = (
        "Find external listings for the requested item.\n"
        f"item_name: {state['item_name']}\n"
        "location_hint: local neighborhood\n"
        "max_distance_km: 5"
    )
    response = agent.run(prompt)
    return _parse_scavenger_response(response.text)

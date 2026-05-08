"""
Scavenger Agent — finds external listings when no local match exists.

Uses the Hack Club AI proxy (OpenAI-compatible) via llm_client.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.services.llm_client import chat_completion

from ..state import OrchestrationState, ScavengerResult


logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    prompt_path = repo_root / "packages" / "prompts" / "scavenger_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


def _parse_scavenger_response(text: str) -> ScavengerResult:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"results": []}

    results = payload.get("results") or []
    return {"results": list(results)}


async def run_scavenger(state: OrchestrationState) -> ScavengerResult:
    """Ask the LLM to find external listings for the requested item."""
    system_prompt = _load_prompt()
    user_prompt = (
        "Find external listings for the requested item.\n"
        f"item_name: {state['item_name']}\n"
        "location_hint: local neighborhood\n"
        "max_distance_km: 5"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    raw_response = chat_completion(messages)
    logger.info("scavenger.llm_response", extra={"response": raw_response[:500]})
    return _parse_scavenger_response(raw_response)

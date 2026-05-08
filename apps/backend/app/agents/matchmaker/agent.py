"""
Matchmaker Agent — queries Supabase, then asks the LLM to pick the best match.

Uses the Hack Club AI proxy (OpenAI-compatible) via llm_client instead of
Google ADK, since we're routing through a custom endpoint.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.services.llm_client import chat_completion
from app.services.supabase_service import SupabaseService

from ..state import MatchmakerResult, OrchestrationState


logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    prompt_path = repo_root / "packages" / "prompts" / "matchmaker_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


def _search_local_inventory(
    item_name: str,
    supabase_svc: SupabaseService,
) -> list[dict]:
    """Query Supabase for available items matching the name."""
    results = supabase_svc.search_items_by_name(item_name)
    matches = []
    for r in results:
        owner_info = r.get("users") or {}
        matches.append({
            "item_id": r.get("id"),
            "item_name": r.get("name"),
            "owner_id": r.get("owner_id"),
            "owner_name": owner_info.get("full_name"),
            "owner_telegram_chat_id": owner_info.get("telegram_chat_id"),
            "description": r.get("description"),
            "category": r.get("category"),
            "condition": r.get("condition"),
            "location_hint": r.get("location_hint"),
        })
    return matches


def _parse_matchmaker_response(text: str) -> MatchmakerResult:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            "success": False,
            "owner_id": None,
            "item_id": None,
            "item_name": None,
            "owner_telegram_chat_id": None,
            "proposed_time": None,
            "reason": "invalid_json",
        }

    return {
        "success": bool(payload.get("success")),
        "owner_id": payload.get("owner_id"),
        "item_id": payload.get("item_id"),
        "item_name": payload.get("item_name"),
        "owner_telegram_chat_id": payload.get("owner_telegram_chat_id"),
        "proposed_time": payload.get("proposed_time"),
        "reason": payload.get("reason"),
    }


async def run_matchmaker(
    state: OrchestrationState,
    supabase_svc: SupabaseService,
) -> MatchmakerResult:
    """
    1. Search Supabase for matching items
    2. If candidates found, ask the LLM to pick the best match
    3. If no candidates, return failure immediately (no LLM call needed)
    """
    item_name = state["item_name"]

    # Step 1: Real Supabase search
    candidates = _search_local_inventory(item_name, supabase_svc)

    if not candidates:
        logger.info("matchmaker.no_candidates", extra={"item_name": item_name})
        return {
            "success": False,
            "owner_id": None,
            "item_id": None,
            "item_name": None,
            "owner_telegram_chat_id": None,
            "proposed_time": None,
            "reason": f"No available items matching '{item_name}' in local inventory",
        }

    # Step 2: Ask LLM to select the best match
    system_prompt = _load_prompt()
    user_prompt = (
        "User request for local matching.\n"
        f"item_name: {item_name}\n"
        f"requested_start: {state['requested_start']}\n"
        f"requested_end: {state['requested_end']}\n"
        f"user_id: {state['user_id']}\n\n"
        f"Available candidates from local inventory:\n"
        f"{json.dumps(candidates, indent=2)}\n\n"
        "Pick the best match and return the JSON response."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    raw_response = chat_completion(messages)
    logger.info("matchmaker.llm_response", extra={"response": raw_response[:500]})

    result = _parse_matchmaker_response(raw_response)

    # If the LLM returned success but missing key fields, fill from first candidate
    if result["success"] and not result["item_id"] and candidates:
        best = candidates[0]
        result["item_id"] = best.get("item_id")
        result["owner_id"] = best.get("owner_id")
        result["item_name"] = best.get("item_name")
        result["owner_telegram_chat_id"] = best.get("owner_telegram_chat_id")

    return result

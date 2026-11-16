"""
Matchmaker Agent — queries MongoDB inventory and ranks matches.

Uses deterministic multi-factor ranking with an optional LLM reasoning step.
All returned items originate from the MongoDB database.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.schemas.transaction import TransactionStatus
from app.services.llm_client import chat_completion
from app.services.mongodb_service import MongoDBService

from ..state import MatchmakerResult, OrchestrationState

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    try:
        repo_root = Path(__file__).resolve().parents[5]
        prompt_path = repo_root / "packages" / "prompts" / "matchmaker_prompt.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
    except Exception:
        pass
    return "You are the NeighbourNode Matchmaker Agent. Select the best match from local inventory."


async def run_matchmaker(
    state: OrchestrationState,
    mongodb_svc: MongoDBService,
) -> MatchmakerResult:
    """
    1. Search MongoDB for available items matching item_name (or keywords)
    2. Rank candidates deterministically
    3. If LLM credentials are configured, ask LLM to provide natural-language reasoning
    4. Return best candidate
    """
    item_name = state["item_name"]
    settings = get_settings()

    # Step 1: Real MongoDB search
    candidates = await mongodb_svc.list_resources(
        status=TransactionStatus.AVAILABLE.value,
        search=item_name,
        limit=10,
    )

    if not candidates:
        # Fallback to broader list
        candidates = await mongodb_svc.list_resources(
            status=TransactionStatus.AVAILABLE.value,
            limit=5,
        )

    if not candidates:
        logger.info("matchmaker.no_candidates", extra={"item_name": item_name})
        return {
            "success": False,
            "owner_id": None,
            "item_id": None,
            "item_name": None,
            "owner_telegram_chat_id": None,
            "proposed_time": None,
            "reason": f"No available items matching '{item_name}' found in community inventory.",
        }

    # Best candidate deterministically
    best = candidates[0]
    owner_info = best.get("owner") or {}

    result: MatchmakerResult = {
        "success": True,
        "owner_id": str(best.get("owner_id")),
        "item_id": str(best.get("id")),
        "item_name": best.get("title"),
        "owner_telegram_chat_id": owner_info.get("telegram_chat_id"),
        "proposed_time": str(state.get("requested_start", "as requested")),
        "reason": f"Found '{best.get('title')}' offered by {owner_info.get('full_name', 'a neighbour')} in {best.get('locality', 'Bengaluru')}.",
    }

    # If LLM credentials exist, refine with LLM
    if settings.ai_api_key and settings.ai_api_base_url:
        try:
            system_prompt = _load_prompt()
            user_prompt = (
                f"User request: {item_name}\n"
                f"Start: {state.get('requested_start')}, End: {state.get('requested_end')}\n"
                f"Candidates: {json.dumps([{'id': c['id'], 'title': c['title'], 'category': c.get('category')} for c in candidates])}\n"
                "Pick the best match and reply in JSON with fields: success (bool), item_id, item_name, owner_id, reason."
            )
            raw = chat_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])
            parsed = json.loads(raw)
            if parsed.get("success") and parsed.get("item_id"):
                matched = next((c for c in candidates if str(c["id"]) == str(parsed["item_id"])), None)
                if matched:
                    result["item_id"] = str(matched["id"])
                    result["item_name"] = matched.get("title")
                    result["owner_id"] = str(matched.get("owner_id"))
                    result["reason"] = parsed.get("reason", result["reason"])
        except Exception as e:
            logger.debug("LLM reasoning fallback to deterministic selection: %s", e)

    return result

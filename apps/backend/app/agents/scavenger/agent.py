"""
Scavenger Agent — searches local MongoDB listings across related categories
when no exact match is found.

External discovery is optional and never fabricates local inventory.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from app.core.config import get_settings
from app.db.mongodb import db, serialize_docs
from app.schemas.transaction import TransactionStatus
from app.services.llm_client import chat_completion

from ..state import OrchestrationState, ScavengerResult

logger = logging.getLogger(__name__)


async def run_scavenger(state: OrchestrationState) -> ScavengerResult:
    """
    Search community inventory across related categories and descriptions.
    """
    item_name = state.get("item_name", "")
    results: List[Dict[str, Any]] = []

    if db.database is not None:
        # Search all active resources in MongoDB matching partial words
        words = [w for w in item_name.split() if len(w) > 2]
        query_parts = [{"title": {"$regex": w, "$options": "i"}} for w in words]
        query_parts.extend([{"description": {"$regex": w, "$options": "i"}} for w in words])

        if query_parts:
            cursor = db.database["resources"].find({
                "$or": query_parts,
                "status": TransactionStatus.AVAILABLE.value,
            }).limit(5)
            docs = await cursor.to_list(length=5)
            for d in docs:
                results.append({
                    "title": d.get("title"),
                    "category": d.get("category"),
                    "locality": d.get("locality", "Bengaluru"),
                    "source": "Local Community Alternative",
                })

    settings = get_settings()
    if not results and settings.ai_api_key and settings.ai_api_base_url:
        try:
            prompt = (
                f"Suggest 2 realistic nearby community alternatives or rental sources in Bengaluru for '{item_name}'. "
                "Return JSON with 'results': list of objects with title, source, estimated_price."
            )
            raw = chat_completion([{"role": "user", "content": prompt}])
            parsed = json.loads(raw)
            if "results" in parsed:
                results = parsed["results"]
        except Exception as e:
            logger.debug("Scavenger external fallback error: %s", e)

    return {"results": results}

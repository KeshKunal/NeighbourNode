"""
AI Assistant route for NeighbourNode (/api/v1/ai/ask).
Interprets natural language queries with deterministic rule-based fallback
and queries real MongoDB listings. Never fabricates candidates.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends

from app.api.dependencies import get_mongodb_service, get_optional_current_user
from app.core.config import get_settings
from app.schemas.api import AIAskRequest, AIAskResponse
from app.schemas.resource import ResourceResponse
from app.schemas.skill import SkillResponse
from app.schemas.users import UserPublicProfile
from app.services.llm_client import chat_completion
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

# Known skill markers for rule-based intent classification
SKILL_MARKERS = [
    "teach", "learn", "tutor", "tutoring", "lesson", "coach", "train", "training",
    "fix", "repair", "guide", "guidance", "class", "programming", "python", "math",
    "guitar", "music", "design", "photography", "fitness"
]

RESOURCE_MARKERS = [
    "borrow", "drill", "ladder", "projector", "tent", "camera", "tool", "tools",
    "equipment", "book", "calculator", "monitor", "cycle", "bicycle", "need a",
    "looking for a", "iron", "cooker", "tripod"
]


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai_assistant(
    payload: AIAskRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> AIAskResponse:
    query = payload.query.strip()
    query_lower = query.lower()

    # Determine intent (skill vs resource)
    skill_score = sum(1 for w in SKILL_MARKERS if w in query_lower)
    resource_score = sum(1 for w in RESOURCE_MARKERS if w in query_lower)
    intent = "skill" if skill_score > resource_score else "resource"

    # Extract keywords (filter out common stopwords)
    stopwords = {"i", "need", "a", "an", "the", "for", "in", "to", "of", "and", "is", "am", "looking", "someone", "who", "can", "near", "my", "tomorrow", "this", "weekend", "evening", "please"}
    tokens = re.findall(r"\b[a-zA-Z]{3,}\b", query_lower)
    keywords = [t for t in tokens if t not in stopwords]
    search_term = " ".join(keywords) if keywords else query

    settings = get_settings()
    matched_resources: List[ResourceResponse] = []
    matched_skills: List[SkillResponse] = []
    matched_neighbours: List[UserPublicProfile] = []

    # Search real MongoDB database
    if intent == "skill":
        # Search skills
        skill_recs = await mongodb_svc.get_recommended_skills(
            query=search_term,
            limit=5,
        )
        matched_skills = [s["skill"] for s in skill_recs]
        if not matched_skills:
            # Fallback search
            skills_raw = await mongodb_svc.list_skills(search=search_term, limit=3)
            matched_skills = [ResourceResponse(**s) if False else SkillResponse(**s) for s in skills_raw]

        explanation = f"Found {len(matched_skills)} community skill provider(s) matching your request for '{search_term}'."
        nl_answer = (
            f"Here are neighbours who offer assistance related to '{query}'. "
            f"You can contact them directly to schedule an exchange session!"
            if matched_skills
            else f"No one is currently offering '{query}' right now, but you can post a community request on the bulletin board."
        )
    else:
        # Search resources
        res_recs = await mongodb_svc.get_recommended_resources(
            query=search_term,
            limit=5,
        )
        matched_resources = [r["resource"] for r in res_recs]
        if not matched_resources:
            # Fallback search
            res_raw = await mongodb_svc.list_resources(search=search_term, limit=3)
            matched_resources = [ResourceResponse(**r) for r in res_raw]

        explanation = f"Matched {len(matched_resources)} available resource(s) in your neighbourhood inventory."
        nl_answer = (
            f"I found {len(matched_resources)} item(s) matching '{query}' available nearby in your community library. "
            f"You can send a borrow request with your preferred pickup time!"
            if matched_resources
            else f"I searched the community library for '{query}', but didn't find an available item right now. You can check back soon or ask neighbours."
        )

    # Optional: Enhance natural language answer with LLM if credentials are configured
    if settings.ai_api_key and settings.ai_api_base_url and (matched_resources or matched_skills):
        try:
            candidates_summary = [
                {"title": r.title, "locality": r.locality, "condition": r.condition}
                for r in matched_resources[:3]
            ] or [
                {"title": s.title, "locality": s.locality, "experience": s.experience_level}
                for s in matched_skills[:3]
            ]
            prompt = (
                f"User asked: '{query}'\n"
                f"We retrieved these actual local items/skills from MongoDB: {json.dumps(candidates_summary)}\n"
                "Write a warm, concise 2-sentence response directly addressing the user. Do not fabricate any new items."
            )
            llm_text = chat_completion([{"role": "user", "content": prompt}])
            if llm_text and len(llm_text) > 10 and not llm_text.startswith("{"):
                nl_answer = llm_text.strip()
        except Exception as e:
            logger.debug("LLM summary enhancement skipped: %s", e)

    return AIAskResponse(
        intent=intent,
        keywords=keywords,
        category=None,
        natural_language_answer=nl_answer,
        matched_resources=matched_resources,
        matched_skills=matched_skills,
        matched_neighbours=matched_neighbours,
        explanation=explanation,
    )


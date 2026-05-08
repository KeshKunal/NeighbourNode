"""
LLM client — wraps the Hack Club AI proxy (OpenAI-compatible endpoint).

Used by agents instead of the Google ADK Agent class, since the ADK
expects native Gemini access and we're routing through a proxy.

Change AI_API_BASE_URL / AI_API_KEY / AI_MODEL in .env to swap models.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings


logger = logging.getLogger(__name__)


def chat_completion(
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]] | None = None,
    model: str | None = None,
) -> str:
    """
    Synchronous chat completion via the Hack Club AI proxy.
    Returns the assistant's message content as a string.

    Supports optional tool definitions for function-calling models.
    """
    settings = get_settings()
    base_url = settings.ai_api_base_url
    api_key = settings.ai_api_key
    model = model or settings.ai_model

    if not base_url or not api_key:
        logger.error("llm.missing_credentials — set AI_API_BASE_URL and AI_API_KEY in .env")
        return json.dumps({"error": "LLM credentials not configured"})

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""
    except httpx.HTTPStatusError as exc:
        logger.error("llm.http_error", extra={"status": exc.response.status_code, "body": exc.response.text[:500]})
        return json.dumps({"error": f"LLM API returned {exc.response.status_code}"})
    except Exception:
        logger.exception("llm.request.failed")
        return json.dumps({"error": "LLM request failed"})

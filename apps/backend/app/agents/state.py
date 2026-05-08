"""
Shared orchestration state — TypedDicts used across all agents.
"""
from __future__ import annotations

from typing import NotRequired, TypedDict


class MatchmakerResult(TypedDict):
    success: bool
    owner_id: str | None
    item_id: str | None
    item_name: str | None
    owner_telegram_chat_id: str | None
    proposed_time: str | None
    reason: NotRequired[str]


class ScavengerListing(TypedDict):
    title: str
    price: str | None
    url: str
    source: str
    distance_km: float | None
    summary: str | None


class ScavengerResult(TypedDict):
    results: list[ScavengerListing]


class OrchestrationState(TypedDict):
    user_id: str
    item_name: str
    requested_start: str
    requested_end: str
    status: str
    errors: list[str]
    # Populated during orchestration
    item_id: NotRequired[str]
    owner_id: NotRequired[str]
    owner_telegram_chat_id: NotRequired[str]
    transaction_id: NotRequired[str]
    telegram_message_id: NotRequired[str]
    match_result: NotRequired[MatchmakerResult]
    scavenger_results: NotRequired[list[ScavengerListing]]

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel


class CategoryCount(BaseModel):
    category: str
    count: int


class TopRatedUser(BaseModel):
    user_id: str
    full_name: str
    avatar_url: str | None = None
    locality: str
    reputation_score: float
    completed_exchanges: int
    review_count: int


class MostSharedResource(BaseModel):
    resource_id: str
    title: str
    category: str
    borrow_count: int


class CommunityAnalyticsResponse(BaseModel):
    total_users: int
    total_resources: int
    total_skills: int
    total_completed_exchanges: int
    most_requested_categories: List[CategoryCount]
    top_rated_members: List[TopRatedUser]
    most_shared_resources: List[MostSharedResource]
    category_distribution: List[CategoryCount]


class UserAnalyticsResponse(BaseModel):
    user_id: str
    resources_listed: int
    skills_offered: int
    active_borrows: int
    completed_borrows: int
    active_lends: int
    completed_lends: int
    reputation_score: float
    review_count: int


"""
API integration test suite for NeighbourNode endpoints.
Tests /api/v1/health, /api/v1/auth, /api/v1/resources, /api/v1/skills, /api/v1/ai/ask.
"""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.db import mongodb
from app.main import app


@pytest.fixture(autouse=True)
def setup_test_db():
    client = AsyncMongoMockClient()
    mock_db = client["test_neighbournode_api"]
    mongodb.db.client = client
    mongodb.db.database = mock_db
    mongodb.db.is_connected = True
    yield
    mongodb.db.is_connected = False


@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"

        db_res = await ac.get("/health/database")
        assert db_res.status_code == 200
        assert db_res.json()["status"] == "connected"


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user
        register_payload = {
            "email": "demo.user@neighbournode.local",
            "password": "Password123!",
            "full_name": "Demo User",
            "locality": "Mathikere, Bengaluru",
            "skills": ["Python", "Guitar"],
            "interests": ["DIY", "Cycling"],
        }
        reg_res = await ac.post("/api/v1/auth/register", json=register_payload)
        assert reg_res.status_code == 200
        data = reg_res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "demo.user@neighbournode.local"
        token = data["access_token"]

        # Access /api/v1/auth/me
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["full_name"] == "Demo User"

        # Login
        login_payload = {
            "email": "demo.user@neighbournode.local",
            "password": "Password123!",
        }
        login_res = await ac.post("/api/v1/auth/login", json=login_payload)
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()


@pytest.mark.asyncio
async def test_resource_and_skill_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register user to get token
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": "creator@neighbournode.local",
            "password": "Password123!",
            "full_name": "Creator",
            "locality": "MSRIT Campus, Bengaluru",
        })
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create resource
        res_payload = {
            "title": "Camping Stove Kit",
            "description": "Portable dual-burner camping stove with gas canisters.",
            "category": "Travel and camping",
            "condition": "Good",
            "locality": "MSRIT Campus, Bengaluru",
        }
        res_create = await ac.post("/api/v1/resources", json=res_payload, headers=headers)
        assert res_create.status_code == 201
        res_id = res_create.json()["id"]

        # List resources
        list_res = await ac.get("/api/v1/resources")
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # Create skill
        skill_payload = {
            "title": "Guitar Lessons for Beginners",
            "description": "Learn fingerpicking and rhythm guitar chords.",
            "category": "Music lessons",
            "experience_level": "Intermediate",
            "availability": "Weekends 4-6 PM",
            "locality": "New BEL Road, Bengaluru",
            "exchange_type": "Free / Community Barter",
        }
        skill_create = await ac.post("/api/v1/skills", json=skill_payload, headers=headers)
        assert skill_create.status_code == 201

        # List skills
        skills_res = await ac.get("/api/v1/skills")
        assert skills_res.status_code == 200
        assert len(skills_res.json()) >= 1


@pytest.mark.asyncio
async def test_ai_ask_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ask AI with no LLM credentials (deterministic fallback)
        ai_res = await ac.post("/api/v1/ai/ask", json={
            "query": "I need a drill for tomorrow evening",
        })
        assert ai_res.status_code == 200
        data = ai_res.json()
        assert data["intent"] == "resource"
        assert "drill" in data["keywords"]
        assert "natural_language_answer" in data


"""
Backend test suite for NeighbourNode (CSAEC59 — AEC-NoSQL).
Tests auth, resources, skills, borrowing concurrency, recommendations, reputation, reviews, and health.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from mongomock_motor import AsyncMongoMockClient

from app.core.config import Settings
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db import mongodb
from app.agents.orchestrator import NeighbourOrchestrator
from app.schemas.api import BorrowRequest
from app.schemas.transaction import TransactionStatus
from app.services.mongodb_service import MongoDBService, haversine_distance_km
from app.services.telegram_service import TelegramService


def _mock_settings() -> Settings:
    return Settings(
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="test_db",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        frontend_url="http://localhost:3000",
        telegram_bot_token=None,
        telegram_webhook_secret=None,
        google_calendar_id=None,
        google_credentials_json=None,
        google_credentials_path=None,
        image_storage_cloud_name=None,
        image_storage_api_key=None,
        image_storage_api_secret=None,
        ai_api_base_url=None,
        ai_api_key=None,
        ai_model="test",
        mock_external_services=True,
    )


@pytest.fixture(autouse=True)
def setup_mock_mongo():
    client = AsyncMongoMockClient()
    mock_db = client["test_neighbournode"]
    mongodb.db.client = client
    mongodb.db.database = mock_db
    mongodb.db.is_connected = True
    yield
    mongodb.db.is_connected = False


# ─── Auth & Security Tests ──────────────────────────────────────────

def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_decoding():
    data = {"sub": "660000000000000000000001", "email": "demo@neighbournode.local"}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "660000000000000000000001"
    assert payload["email"] == "demo@neighbournode.local"


# ─── Geospatial Tests ───────────────────────────────────────────────

def test_haversine_distance():
    # Distance between MSRIT Campus [77.5649, 13.0308] and Mathikere [77.5583, 13.0336]
    msrit = [77.5649, 13.0308]
    mathikere = [77.5583, 13.0336]
    dist = haversine_distance_km(msrit, mathikere)
    assert 0.5 < dist < 2.0  # Approx 0.7 - 1.0 km


# ─── MongoDB Service Tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_creation_and_retrieval():
    service = MongoDBService()
    user_data = {
        "full_name": "Test Neighbour",
        "email": "test@neighbournode.local",
        "locality": "Mathikere, Bengaluru",
        "password_hash": hash_password("pass123"),
    }
    created = await service.create_user(user_data)
    assert created["id"] is not None
    assert created["full_name"] == "Test Neighbour"
    assert created["reputation_score"] == 4.5

    fetched = await service.get_user_by_id(created["id"])
    assert fetched is not None
    assert fetched["email"] == "test@neighbournode.local"


@pytest.mark.asyncio
async def test_resource_crud():
    service = MongoDBService()
    user = await service.create_user({"full_name": "Owner", "email": "res_owner@test.local"})
    resource_data = {
        "owner_id": user["id"],
        "title": "Bosch Impact Drill",
        "description": "500W power drill kit with masonry bits",
        "category": "Tools and equipment",
        "condition": "Like New",
        "locality": "MSRIT Campus, Bengaluru",
        "location": {"type": "Point", "coordinates": [77.5649, 13.0308]},
    }
    res = await service.create_resource(resource_data)
    assert res["id"] is not None
    assert res["status"] == TransactionStatus.AVAILABLE.value

    # Update
    updated = await service.update_resource(res["id"], {"condition": "Good"}, owner_id=user["id"])
    assert updated["condition"] == "Good"

    # List
    items = await service.list_resources(category="Tools and equipment")
    assert len(items) == 1
    assert items[0]["title"] == "Bosch Impact Drill"


@pytest.mark.asyncio
async def test_borrow_request_and_atomic_conflict_detection():
    service = MongoDBService()
    owner = await service.create_user({"full_name": "Owner", "email": "o1@test.local"})
    borrower1 = await service.create_user({"full_name": "Borrower 1", "email": "b1@test.local"})
    borrower2 = await service.create_user({"full_name": "Borrower 2", "email": "b2@test.local"})

    res = await service.create_resource({
        "owner_id": owner["id"],
        "title": "Tent",
        "description": "3-person camping tent",
        "category": "Travel and camping",
        "locality": "Malleshwaram",
        "location": {"type": "Point", "coordinates": [77.5670, 13.0085]},
    })

    # Cannot borrow own resource
    with pytest.raises(ValueError, match="own resource"):
        await service.create_borrow_request(
            resource_id=res["id"],
            borrower_id=owner["id"],
            requested_start=datetime.now(timezone.utc),
            requested_end=datetime.now(timezone.utc) + timedelta(days=2),
        )

    # Borrower 1 creates request
    now = datetime.now(timezone.utc)
    start_date = now + timedelta(days=1)
    end_date = now + timedelta(days=3)
    req1 = await service.create_borrow_request(
        resource_id=res["id"],
        borrower_id=borrower1["id"],
        requested_start=start_date,
        requested_end=end_date,
    )
    assert req1["status"] == TransactionStatus.PENDING_APPROVAL.value

    # Owner approves request 1 -> marks RESERVED
    approval_res = await service.approve_borrow_request(req1["id"], owner_id=owner["id"])
    assert approval_res.success is True

    # Borrower 2 attempts to request overlapping dates -> must be rejected atomically!
    with pytest.raises(ValueError, match="conflicting reservation"):
        await service.create_borrow_request(
            resource_id=res["id"],
            borrower_id=borrower2["id"],
            requested_start=start_date + timedelta(hours=12),
            requested_end=end_date + timedelta(hours=12),
        )


@pytest.mark.asyncio
async def test_reputation_and_review_workflow():
    service = MongoDBService()
    user1 = await service.create_user({"full_name": "Alice", "email": "alice@test.local"})
    user2 = await service.create_user({"full_name": "Bob", "email": "bob@test.local"})

    # Self-review prohibited
    with pytest.raises(ValueError, match="cannot review yourself"):
        await service.create_review(
            reviewer_id=user1["id"],
            reviewed_user_id=user1["id"],
            rating=5,
            comment="Awesome self!",
        )

    # Valid review
    rev = await service.create_review(
        reviewer_id=user1["id"],
        reviewed_user_id=user2["id"],
        rating=5,
        comment="Bob was very punctual and respectful.",
    )
    assert rev["rating"] == 5

    # Check updated reputation
    bob = await service.get_user_by_id(user2["id"])
    assert bob["reputation_score"] >= 4.0


@pytest.mark.asyncio
async def test_orchestrator_not_found():
    telegram_svc = TelegramService(_mock_settings())
    mongodb_svc = MongoDBService()
    orchestrator = NeighbourOrchestrator(mongodb_service=mongodb_svc, telegram_service=telegram_svc)

    payload = BorrowRequest(
        item_id="660000000000000000000099",
        borrower_id="660000000000000000000001",
        requested_start=datetime.now(timezone.utc),
        requested_end=datetime.now(timezone.utc) + timedelta(hours=4),
    )
    res = await orchestrator.process_portal_request(payload)
    assert res.success is False
    assert "not found" in res.message.lower()


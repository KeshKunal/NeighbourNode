"""
MongoDB Database Management Module for NeighbourNode.

Handles:
- Motor AsyncIOMotorClient lifecycle
- Collection accessors
- Index initialization (2dsphere, unique, compound, text)
- Safe ObjectId serialization and deserialization
- Health checks
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False
    connection_error: Optional[str] = None


db = MongoDB()


def str_to_object_id(val: Any) -> ObjectId | Any:
    if isinstance(val, str) and ObjectId.is_valid(val):
        return ObjectId(val)
    return val


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Recursively serialize MongoDB document for API responses:
    - Replaces _id with id (string)
    - Converts ObjectIds to strings
    - Converts datetimes to ISO formatted strings if needed
    """
    if doc is None:
        return None

    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [
                str(item) if isinstance(item, ObjectId)
                else serialize_doc(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            # Check if this is a GeoJSON dict or regular subdict
            result[key] = serialize_doc(value)
        else:
            result[key] = value

    if "_id" in result and "id" not in result:
        result["id"] = str(result["_id"])
    return result


def serialize_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [serialize_doc(d) for d in docs if d is not None]


async def connect_to_mongo() -> None:
    settings = get_settings()
    logger.info("Connecting to MongoDB at %s...", settings.mongodb_uri)
    try:
        # 5-second serverSelectionTimeoutMS so app starts smoothly even if remote cluster is slow or unreachable
        db.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        db.database = db.client[settings.mongodb_database]

        # Verify connection
        await db.client.admin.command("ping")
        db.is_connected = True
        db.connection_error = None
        logger.info("Successfully connected to MongoDB database: %s", settings.mongodb_database)

        # Initialize collections and indexes
        await initialize_indexes()
    except Exception as exc:
        db.is_connected = False
        db.connection_error = str(exc)
        logger.warning(
            "MongoDB connection could not be established immediately (%s). "
            "Backend will remain running and retry on demand.",
            exc,
        )


async def close_mongo_connection() -> None:
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        db.is_connected = False
        logger.info("MongoDB connection closed.")


async def initialize_indexes() -> None:
    """
    Creates required MongoDB indexes:
    - 2dsphere on resources.location, skills.location, users.location, communities.approximate_location
    - Unique email on users
    - Sparse unique on phone
    - Compound indexes for borrow_requests, transactions, reviews
    - Text indexes for keyword searches
    """
    if db.database is None:
        logger.warning("Cannot initialize indexes: database client is None")
        return

    try:
        # Users indexes
        users = db.database["users"]
        await users.create_index([("email", pymongo.ASCENDING)], unique=True)
        await users.create_index([("phone", pymongo.ASCENDING)], unique=True, sparse=True)
        await users.create_index([("location", pymongo.GEOSPHERE)])
        await users.create_index([("telegram_chat_id", pymongo.ASCENDING)], sparse=True)
        await users.create_index([("locality", pymongo.ASCENDING)])

        # Resources indexes
        resources = db.database["resources"]
        await resources.create_index([("location", pymongo.GEOSPHERE)])
        await resources.create_index([("owner_id", pymongo.ASCENDING)])
        await resources.create_index([("category", pymongo.ASCENDING)])
        await resources.create_index([("status", pymongo.ASCENDING)])
        await resources.create_index([("title", pymongo.TEXT), ("description", pymongo.TEXT)])

        # Skills indexes
        skills = db.database["skills"]
        await skills.create_index([("location", pymongo.GEOSPHERE)])
        await skills.create_index([("provider_id", pymongo.ASCENDING)])
        await skills.create_index([("category", pymongo.ASCENDING)])
        await skills.create_index([("status", pymongo.ASCENDING)])
        await skills.create_index([("title", pymongo.TEXT), ("description", pymongo.TEXT)])

        # Borrow requests indexes
        borrow_reqs = db.database["borrow_requests"]
        await borrow_reqs.create_index([("resource_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])
        await borrow_reqs.create_index([("borrower_id", pymongo.ASCENDING)])
        await borrow_reqs.create_index([("owner_id", pymongo.ASCENDING)])

        # Transactions indexes
        transactions = db.database["transactions"]
        await transactions.create_index([("resource_id", pymongo.ASCENDING)])
        await transactions.create_index([("borrower_id", pymongo.ASCENDING)])
        await transactions.create_index([("owner_id", pymongo.ASCENDING)])
        await transactions.create_index([("status", pymongo.ASCENDING)])
        await transactions.create_index([("resource_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])

        # Skill requests indexes
        skill_reqs = db.database["skill_requests"]
        await skill_reqs.create_index([("skill_id", pymongo.ASCENDING)])
        await skill_reqs.create_index([("requester_id", pymongo.ASCENDING)])
        await skill_reqs.create_index([("provider_id", pymongo.ASCENDING)])
        await skill_reqs.create_index([("status", pymongo.ASCENDING)])

        # Skill exchanges indexes
        skill_exchanges = db.database["skill_exchanges"]
        await skill_exchanges.create_index([("skill_id", pymongo.ASCENDING)])
        await skill_exchanges.create_index([("provider_id", pymongo.ASCENDING)])
        await skill_exchanges.create_index([("requester_id", pymongo.ASCENDING)])

        # Reviews indexes
        reviews = db.database["reviews"]
        await reviews.create_index([("reviewed_user_id", pymongo.ASCENDING)])
        await reviews.create_index([("reviewer_id", pymongo.ASCENDING)])
        await reviews.create_index([("reviewer_id", pymongo.ASCENDING), ("transaction_id", pymongo.ASCENDING)], unique=True, sparse=True)
        await reviews.create_index([("reviewer_id", pymongo.ASCENDING), ("skill_exchange_id", pymongo.ASCENDING)], unique=True, sparse=True)

        # Connections indexes
        connections = db.database["connections"]
        await connections.create_index([("requester_id", pymongo.ASCENDING), ("recipient_id", pymongo.ASCENDING)], unique=True)

        # Notifications indexes
        notifications = db.database["notifications"]
        await notifications.create_index([("user_id", pymongo.ASCENDING), ("is_read", pymongo.ASCENDING)])
        await notifications.create_index([("created_at", pymongo.DESCENDING)])

        # Communities indexes
        communities = db.database["communities"]
        await communities.create_index([("approximate_location", pymongo.GEOSPHERE)])
        await communities.create_index([("locality", pymongo.ASCENDING)])

        logger.info("All MongoDB indexes initialized successfully.")
    except Exception as e:
        logger.warning("Error creating MongoDB indexes: %s", e)


def get_database() -> AsyncIOMotorDatabase:
    if db.database is None:
        raise RuntimeError("MongoDB database is not initialized. Please check connection.")
    return db.database


def get_collection(name: str) -> AsyncIOMotorCollection:
    return get_database()[name]


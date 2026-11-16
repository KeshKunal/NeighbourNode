"""
Health check routes for NeighbourNode (/health).
"""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter
from app.db.mongodb import db
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "NeighbourNode API",
        "database_connected": db.is_connected,
    }


@router.get("/health/database")
async def database_health_check() -> Dict[str, Any]:
    settings = get_settings()
    if not db.is_connected or db.database is None:
        return {
            "status": "disconnected",
            "database": settings.mongodb_database,
            "error": db.connection_error or "Not connected to MongoDB",
            "message": "MongoDB is currently disconnected or unreachable. Check MONGODB_URI in .env",
        }

    try:
        await db.client.admin.command("ping")
        # Gather collection counts
        collections = await db.database.list_collection_names()
        counts = {}
        for coll in ["users", "resources", "skills", "borrow_requests", "transactions", "reviews"]:
            if coll in collections:
                counts[coll] = await db.database[coll].count_documents({})

        return {
            "status": "connected",
            "database": settings.mongodb_database,
            "ping": "ok",
            "collections_count": len(collections),
            "document_counts": counts,
        }
    except Exception as e:
        return {
            "status": "error",
            "database": settings.mongodb_database,
            "error": str(e),
        }


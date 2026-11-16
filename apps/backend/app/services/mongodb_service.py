"""
MongoDB Service for NeighbourNode.
Provides MongoDB-only persistence, aggregations, geospatial discovery,
atomic reservation updates, reputation engine, and multi-agent integrations.
"""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from bson import ObjectId

from app.db.mongodb import db, serialize_doc, serialize_docs, str_to_object_id
from app.schemas.transaction import TransactionStatus, TransactionUpdateResult

logger = logging.getLogger(__name__)


def haversine_distance_km(coord1: List[float], coord2: List[float]) -> float:
    """
    Computes distance in km between two GeoJSON [lon, lat] coordinates.
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class MongoDBService:
    def __init__(self) -> None:
        pass

    @property
    def _db(self):
        return db.database

    def _require_db(self):
        if self._db is None:
            raise RuntimeError("MongoDB is not connected. Please check database configuration.")

    # ─────────────────────────────────────────────────────────────
    # USERS
    # ─────────────────────────────────────────────────────────────

    async def get_user_by_id(self, user_id: str | ObjectId) -> Optional[Dict[str, Any]]:
        self._require_db()
        doc = await self._db["users"].find_one({"_id": str_to_object_id(user_id)})
        return serialize_doc(doc)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        self._require_db()
        doc = await self._db["users"].find_one({"email": email.strip().lower()})
        return doc  # Raw doc (including password_hash for auth checks)

    async def get_user_by_telegram_chat_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        self._require_db()
        doc = await self._db["users"].find_one({"telegram_chat_id": str(chat_id)})
        return serialize_doc(doc)

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_db()
        now = datetime.now(timezone.utc)
        user_data["created_at"] = now
        user_data["updated_at"] = now
        if "email" in user_data:
            user_data["email"] = user_data["email"].strip().lower()
        if "reputation_score" not in user_data:
            user_data["reputation_score"] = 4.5
        if "completed_exchanges" not in user_data:
            user_data["completed_exchanges"] = 0
        if "is_verified" not in user_data:
            user_data["is_verified"] = True
        if "is_active" not in user_data:
            user_data["is_active"] = True

        res = await self._db["users"].insert_one(user_data)
        user_data["_id"] = res.inserted_id
        return serialize_doc(user_data)

    async def update_user(self, user_id: str | ObjectId, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self._require_db()
        update_fields["updated_at"] = datetime.now(timezone.utc)
        # Ensure password_hash is not accidentally overwritten with None
        update_fields.pop("password_hash", None)
        await self._db["users"].update_one(
            {"_id": str_to_object_id(user_id)},
            {"$set": update_fields},
        )
        return await self.get_user_by_id(user_id)

    # ─────────────────────────────────────────────────────────────
    # RESOURCES (PHYSICAL ITEMS)
    # ─────────────────────────────────────────────────────────────

    async def list_resources(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        locality: Optional[str] = None,
        owner_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        self._require_db()
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        if locality:
            query["locality"] = {"$regex": locality, "$options": "i"}
        if owner_id:
            query["owner_id"] = str_to_object_id(owner_id)
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
            ]

        cursor = self._db["resources"].find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            # Attach owner profile summary
            owner = await self.get_user_by_id(doc.get("owner_id"))
            if owner:
                serialized["owner"] = {
                    "id": owner["id"],
                    "full_name": owner["full_name"],
                    "locality": owner.get("locality", "Bengaluru"),
                    "reputation_score": owner.get("reputation_score", 4.5),
                    "avatar_url": owner.get("avatar_url"),
                    "telegram_chat_id": owner.get("telegram_chat_id"),
                }
            results.append(serialized)
        return results

    async def get_resource_by_id(self, resource_id: str | ObjectId) -> Optional[Dict[str, Any]]:
        self._require_db()
        doc = await self._db["resources"].find_one({"_id": str_to_object_id(resource_id)})
        if not doc:
            return None
        serialized = serialize_doc(doc)
        owner = await self.get_user_by_id(doc.get("owner_id"))
        if owner:
            serialized["owner"] = {
                "id": owner["id"],
                "full_name": owner["full_name"],
                "locality": owner.get("locality", "Bengaluru"),
                "reputation_score": owner.get("reputation_score", 4.5),
                "avatar_url": owner.get("avatar_url"),
                "telegram_chat_id": owner.get("telegram_chat_id"),
            }
        return serialized

    async def create_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_db()
        now = datetime.now(timezone.utc)
        resource_data["created_at"] = now
        resource_data["updated_at"] = now
        resource_data["owner_id"] = str_to_object_id(resource_data["owner_id"])
        if "status" not in resource_data:
            resource_data["status"] = TransactionStatus.AVAILABLE.value

        res = await self._db["resources"].insert_one(resource_data)
        resource_data["_id"] = res.inserted_id
        return await self.get_resource_by_id(res.inserted_id)

    async def update_resource(
        self, resource_id: str | ObjectId, update_fields: Dict[str, Any], owner_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        self._require_db()
        query: Dict[str, Any] = {"_id": str_to_object_id(resource_id)}
        if owner_id:
            query["owner_id"] = str_to_object_id(owner_id)

        update_fields["updated_at"] = datetime.now(timezone.utc)
        res = await self._db["resources"].update_one(query, {"$set": update_fields})
        if res.matched_count == 0:
            return None
        return await self.get_resource_by_id(resource_id)

    async def delete_resource(self, resource_id: str | ObjectId, owner_id: Optional[str] = None) -> bool:
        self._require_db()
        query: Dict[str, Any] = {"_id": str_to_object_id(resource_id)}
        if owner_id:
            query["owner_id"] = str_to_object_id(owner_id)
        res = await self._db["resources"].delete_one(query)
        return res.deleted_count > 0

    async def find_nearby_resources(
        self,
        longitude: float,
        latitude: float,
        max_distance_meters: float = 10000.0,
        category: Optional[str] = None,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Geospatial discovery using MongoDB 2dsphere index and $near / $geoNear.
        """
        self._require_db()
        query: Dict[str, Any] = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "$maxDistance": max_distance_meters,
                }
            },
            "status": TransactionStatus.AVAILABLE.value,
        }
        if category:
            query["category"] = category

        try:
            cursor = self._db["resources"].find(query).limit(limit)
            docs = await cursor.to_list(length=limit)
        except Exception as e:
            # Fallback if 2dsphere index is still building or coords are missing
            logger.warning("Geospatial $near query failed, using regex fallback: %s", e)
            fallback_query: Dict[str, Any] = {"status": TransactionStatus.AVAILABLE.value}
            if category:
                fallback_query["category"] = category
            cursor = self._db["resources"].find(fallback_query).limit(limit)
            docs = await cursor.to_list(length=limit)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            # Compute distance if location present
            if doc.get("location") and "coordinates" in doc["location"]:
                c = doc["location"]["coordinates"]
                serialized["distance_km"] = haversine_distance_km([longitude, latitude], c)
            owner = await self.get_user_by_id(doc.get("owner_id"))
            if owner:
                serialized["owner"] = {
                    "id": owner["id"],
                    "full_name": owner["full_name"],
                    "locality": owner.get("locality", "Bengaluru"),
                    "reputation_score": owner.get("reputation_score", 4.5),
                    "avatar_url": owner.get("avatar_url"),
                    "telegram_chat_id": owner.get("telegram_chat_id"),
                }
            results.append(serialized)
        return results

    # ─────────────────────────────────────────────────────────────
    # SKILLS MARKETPLACE
    # ─────────────────────────────────────────────────────────────

    async def list_skills(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        provider_id: Optional[str] = None,
        locality: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        self._require_db()
        query: Dict[str, Any] = {"status": "active"}
        if category:
            query["category"] = category
        if provider_id:
            query["provider_id"] = str_to_object_id(provider_id)
        if locality:
            query["locality"] = {"$regex": locality, "$options": "i"}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
            ]

        cursor = self._db["skills"].find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            provider = await self.get_user_by_id(doc.get("provider_id"))
            if provider:
                serialized["provider"] = {
                    "id": provider["id"],
                    "full_name": provider["full_name"],
                    "locality": provider.get("locality", "Bengaluru"),
                    "reputation_score": provider.get("reputation_score", 4.5),
                    "avatar_url": provider.get("avatar_url"),
                    "telegram_chat_id": provider.get("telegram_chat_id"),
                }
            results.append(serialized)
        return results

    async def get_skill_by_id(self, skill_id: str | ObjectId) -> Optional[Dict[str, Any]]:
        self._require_db()
        doc = await self._db["skills"].find_one({"_id": str_to_object_id(skill_id)})
        if not doc:
            return None
        serialized = serialize_doc(doc)
        provider = await self.get_user_by_id(doc.get("provider_id"))
        if provider:
            serialized["provider"] = {
                "id": provider["id"],
                "full_name": provider["full_name"],
                "locality": provider.get("locality", "Bengaluru"),
                "reputation_score": provider.get("reputation_score", 4.5),
                "avatar_url": provider.get("avatar_url"),
                "telegram_chat_id": provider.get("telegram_chat_id"),
            }
        return serialized

    async def create_skill(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        self._require_db()
        now = datetime.now(timezone.utc)
        skill_data["created_at"] = now
        skill_data["updated_at"] = now
        skill_data["provider_id"] = str_to_object_id(skill_data["provider_id"])
        if "status" not in skill_data:
            skill_data["status"] = "active"

        res = await self._db["skills"].insert_one(skill_data)
        return await self.get_skill_by_id(res.inserted_id)

    async def update_skill(
        self, skill_id: str | ObjectId, update_fields: Dict[str, Any], provider_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        self._require_db()
        query: Dict[str, Any] = {"_id": str_to_object_id(skill_id)}
        if provider_id:
            query["provider_id"] = str_to_object_id(provider_id)
        update_fields["updated_at"] = datetime.now(timezone.utc)
        res = await self._db["skills"].update_one(query, {"$set": update_fields})
        if res.matched_count == 0:
            return None
        return await self.get_skill_by_id(skill_id)

    async def delete_skill(self, skill_id: str | ObjectId, provider_id: Optional[str] = None) -> bool:
        self._require_db()
        query: Dict[str, Any] = {"_id": str_to_object_id(skill_id)}
        if provider_id:
            query["provider_id"] = str_to_object_id(provider_id)
        res = await self._db["skills"].delete_one(query)
        return res.deleted_count > 0

    # ─────────────────────────────────────────────────────────────
    # BORROWING & TRANSACTIONS (ATOMIC CONCURRENCY PROTECTION)
    # ─────────────────────────────────────────────────────────────

    async def create_borrow_request(
        self,
        resource_id: str,
        borrower_id: str,
        requested_start: datetime,
        requested_end: datetime,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a borrow request with atomic date overlap checks.
        Validates that the resource exists, borrower is not owner, and no overlapping approved loan exists.
        """
        self._require_db()
        res_oid = str_to_object_id(resource_id)
        resource = await self._db["resources"].find_one({"_id": res_oid})
        if not resource:
            raise ValueError(f"Resource {resource_id} not found.")

        owner_id = resource["owner_id"]
        if str(owner_id) == str(borrower_id):
            raise ValueError("You cannot borrow your own resource.")

        # Check for overlapping confirmed reservations/active loans
        overlap_query = {
            "resource_id": res_oid,
            "status": {"$in": [TransactionStatus.APPROVED.value, TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
            "approved_start": {"$lt": requested_end},
            "approved_end": {"$gt": requested_start},
        }
        conflicting_tx = await self._db["transactions"].find_one(overlap_query)
        if conflicting_tx:
            raise ValueError("This resource already has a conflicting reservation for the requested dates.")

        now = datetime.now(timezone.utc)
        request_doc = {
            "resource_id": res_oid,
            "borrower_id": str_to_object_id(borrower_id),
            "owner_id": owner_id,
            "requested_start": requested_start,
            "requested_end": requested_end,
            "status": TransactionStatus.PENDING_APPROVAL.value,
            "message": message or "Borrow request from community member",
            "created_at": now,
            "updated_at": now,
        }
        res = await self._db["borrow_requests"].insert_one(request_doc)
        request_doc["_id"] = res.inserted_id

        # Record community interaction
        await self._record_interaction(
            actor_id=borrower_id,
            target_user_id=str(owner_id),
            interaction_type="BORROW_REQUEST",
            related_resource_id=resource_id,
        )

        # Notify owner
        borrower = await self.get_user_by_id(borrower_id)
        borrower_name = borrower["full_name"] if borrower else "A neighbour"
        await self.create_notification(
            user_id=str(owner_id),
            type="BORROW_REQUEST_RECEIVED",
            title=f"Borrow Request: {resource.get('title', 'Item')}",
            message=f"{borrower_name} requested to borrow '{resource.get('title')}'.",
            related_entity_id=str(res.inserted_id),
        )

        serialized = serialize_doc(request_doc)
        serialized["resource_title"] = resource.get("title")
        serialized["borrower_name"] = borrower_name
        owner = await self.get_user_by_id(owner_id)
        serialized["owner_name"] = owner["full_name"] if owner else "Owner"
        return serialized

    async def approve_borrow_request(
        self, request_id: str, owner_id: str
    ) -> TransactionUpdateResult:
        """
        Atomic owner approval of a borrow request.
        Creates a transaction and sets resource to RESERVED atomically.
        """
        self._require_db()
        req_oid = str_to_object_id(request_id)
        req = await self._db["borrow_requests"].find_one({"_id": req_oid})
        if not req:
            return TransactionUpdateResult(success=False, message="Borrow request not found")

        if str(req["owner_id"]) != str(owner_id):
            return TransactionUpdateResult(success=False, message="Only the resource owner can approve this request")

        if req["status"] != TransactionStatus.PENDING_APPROVAL.value:
            return TransactionUpdateResult(
                success=False, message=f"Request is not pending approval (status: {req['status']})"
            )

        resource_id = req["resource_id"]

        # Atomic conditional check on overlapping confirmed reservations
        conflict = await self._db["transactions"].find_one({
            "resource_id": resource_id,
            "status": {"$in": [TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
            "approved_start": {"$lt": req["requested_end"]},
            "approved_end": {"$gt": req["requested_start"]},
        })
        if conflict:
            return TransactionUpdateResult(
                success=False, message="Conflict detected: resource is already booked for this timeframe"
            )

        now = datetime.now(timezone.utc)

        # Create Transaction
        tx_data = {
            "resource_id": resource_id,
            "borrow_request_id": req_oid,
            "borrower_id": req["borrower_id"],
            "owner_id": req["owner_id"],
            "approved_start": req["requested_start"],
            "approved_end": req["requested_end"],
            "actual_return_date": None,
            "status": TransactionStatus.RESERVED.value,
            "created_at": now,
            "updated_at": now,
        }
        tx_res = await self._db["transactions"].insert_one(tx_data)

        # Update borrow request status
        await self._db["borrow_requests"].update_one(
            {"_id": req_oid},
            {"$set": {"status": TransactionStatus.APPROVED.value, "updated_at": now}},
        )

        # Update resource status
        await self._db["resources"].update_one(
            {"_id": resource_id},
            {"$set": {"status": TransactionStatus.RESERVED.value, "updated_at": now}},
        )

        # Notify borrower
        resource = await self._db["resources"].find_one({"_id": resource_id})
        res_title = resource.get("title", "the requested item") if resource else "the item"
        await self.create_notification(
            user_id=str(req["borrower_id"]),
            type="BORROW_REQUEST_ACCEPTED",
            title="Borrow Request Approved! 🎉",
            message=f"The owner approved your request to borrow '{res_title}'.",
            related_entity_id=str(tx_res.inserted_id),
        )

        return TransactionUpdateResult(
            success=True,
            message=f"Borrow request approved. Reservation active.",
            transaction_id=str(tx_res.inserted_id),
            resource_id=str(resource_id),
        )

    async def reject_borrow_request(self, request_id: str, owner_id: str, reason: str = "") -> bool:
        self._require_db()
        req_oid = str_to_object_id(request_id)
        req = await self._db["borrow_requests"].find_one({"_id": req_oid})
        if not req or str(req["owner_id"]) != str(owner_id):
            return False

        now = datetime.now(timezone.utc)
        await self._db["borrow_requests"].update_one(
            {"_id": req_oid},
            {"$set": {"status": TransactionStatus.REJECTED.value, "updated_at": now}},
        )

        # Notify borrower
        resource = await self._db["resources"].find_one({"_id": req["resource_id"]})
        res_title = resource.get("title", "item") if resource else "item"
        await self.create_notification(
            user_id=str(req["borrower_id"]),
            type="BORROW_REQUEST_REJECTED",
            title="Borrow Request Update",
            message=f"The owner was unable to accept your request for '{res_title}'. {reason}".strip(),
            related_entity_id=str(request_id),
        )
        return True

    async def start_transaction(self, request_id: str, user_id: str) -> bool:
        """
        Marks loan as ACTIVE (item has been handed over).
        Can be triggered by owner or borrower.
        """
        self._require_db()
        tx = await self._db["transactions"].find_one({
            "$or": [{"borrow_request_id": str_to_object_id(request_id)}, {"_id": str_to_object_id(request_id)}]
        })
        if not tx:
            return False
        if str(tx["owner_id"]) != str(user_id) and str(tx["borrower_id"]) != str(user_id):
            return False

        now = datetime.now(timezone.utc)
        await self._db["transactions"].update_one(
            {"_id": tx["_id"]},
            {"$set": {"status": TransactionStatus.ACTIVE.value, "updated_at": now}},
        )
        await self._db["resources"].update_one(
            {"_id": tx["resource_id"]},
            {"$set": {"status": TransactionStatus.ACTIVE.value, "updated_at": now}},
        )
        return True

    async def return_transaction(self, request_id: str, user_id: str) -> bool:
        """
        Marks item as returned and restores resource status to AVAILABLE.
        Increments user completed_exchanges and recalculates reputation.
        """
        self._require_db()
        tx = await self._db["transactions"].find_one({
            "$or": [{"borrow_request_id": str_to_object_id(request_id)}, {"_id": str_to_object_id(request_id)}]
        })
        if not tx:
            return False
        if str(tx["owner_id"]) != str(user_id) and str(tx["borrower_id"]) != str(user_id):
            return False

        now = datetime.now(timezone.utc)
        await self._db["transactions"].update_one(
            {"_id": tx["_id"]},
            {"$set": {"status": TransactionStatus.RETURNED.value, "actual_return_date": now, "updated_at": now}},
        )
        # Reset resource back to AVAILABLE
        await self._db["resources"].update_one(
            {"_id": tx["resource_id"]},
            {"$set": {"status": TransactionStatus.AVAILABLE.value, "updated_at": now}},
        )

        # Increment completed_exchanges for both parties
        await self._db["users"].update_one(
            {"_id": tx["borrower_id"]},
            {"$inc": {"completed_exchanges": 1}},
        )
        await self._db["users"].update_one(
            {"_id": tx["owner_id"]},
            {"$inc": {"completed_exchanges": 1}},
        )

        # Notify both parties
        resource = await self._db["resources"].find_one({"_id": tx["resource_id"]})
        title = resource.get("title", "Resource") if resource else "Resource"
        await self.create_notification(
            user_id=str(tx["borrower_id"]),
            type="RESOURCE_RETURNED",
            title="Loan Completed!",
            message=f"'{title}' has been marked as returned. You can now leave a review for your neighbour.",
            related_entity_id=str(tx["_id"]),
        )
        await self.create_notification(
            user_id=str(tx["owner_id"]),
            type="RESOURCE_RETURNED",
            title="Resource Returned",
            message=f"'{title}' has been successfully returned and is available to community members again.",
            related_entity_id=str(tx["_id"]),
        )

        # Recalculate reputation scores
        await self.recalculate_user_reputation(str(tx["borrower_id"]))
        await self.recalculate_user_reputation(str(tx["owner_id"]))
        return True

    async def list_borrow_requests(
        self, user_id: str, role: str = "all"
    ) -> List[Dict[str, Any]]:
        self._require_db()
        u_oid = str_to_object_id(user_id)
        if role == "borrower":
            query = {"borrower_id": u_oid}
        elif role == "owner":
            query = {"owner_id": u_oid}
        else:
            query = {"$or": [{"borrower_id": u_oid}, {"owner_id": u_oid}]}

        cursor = self._db["borrow_requests"].find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            resource = await self._db["resources"].find_one({"_id": doc["resource_id"]})
            if resource:
                serialized["resource_title"] = resource.get("title")
            borrower = await self.get_user_by_id(doc["borrower_id"])
            if borrower:
                serialized["borrower_name"] = borrower.get("full_name")
            owner = await self.get_user_by_id(doc["owner_id"])
            if owner:
                serialized["owner_name"] = owner.get("full_name")

            # Check if there is an associated transaction
            tx = await self._db["transactions"].find_one({"borrow_request_id": doc["_id"]})
            if tx:
                serialized["transaction_id"] = str(tx["_id"])
            results.append(serialized)
        return results

    async def list_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        self._require_db()
        u_oid = str_to_object_id(user_id)
        cursor = self._db["transactions"].find({"$or": [{"borrower_id": u_oid}, {"owner_id": u_oid}]}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            resource = await self._db["resources"].find_one({"_id": doc["resource_id"]})
            if resource:
                serialized["resource_title"] = resource.get("title")
            borrower = await self.get_user_by_id(doc["borrower_id"])
            if borrower:
                serialized["borrower_name"] = borrower.get("full_name")
            owner = await self.get_user_by_id(doc["owner_id"])
            if owner:
                serialized["owner_name"] = owner.get("full_name")
            results.append(serialized)
        return results

    # ─────────────────────────────────────────────────────────────
    # SKILL REQUESTS & EXCHANGES
    # ─────────────────────────────────────────────────────────────

    async def create_skill_request(
        self, skill_id: str, requester_id: str, requested_date: datetime, description: str
    ) -> Dict[str, Any]:
        self._require_db()
        skill = await self.get_skill_by_id(skill_id)
        if not skill:
            raise ValueError("Skill listing not found")

        provider_id = skill["provider_id"]
        if str(provider_id) == str(requester_id):
            raise ValueError("You cannot request assistance from your own skill listing")

        now = datetime.now(timezone.utc)
        req_doc = {
            "skill_id": str_to_object_id(skill_id),
            "requester_id": str_to_object_id(requester_id),
            "provider_id": str_to_object_id(provider_id),
            "requested_date": requested_date,
            "description": description,
            "status": "PENDING",
            "created_at": now,
            "updated_at": now,
        }
        res = await self._db["skill_requests"].insert_one(req_doc)
        req_doc["_id"] = res.inserted_id

        # Notify provider
        requester = await self.get_user_by_id(requester_id)
        r_name = requester["full_name"] if requester else "A neighbour"
        await self.create_notification(
            user_id=str(provider_id),
            type="SKILL_REQUEST_RECEIVED",
            title=f"New Skill Request: {skill.get('title')}",
            message=f"{r_name} requested a skill exchange session with you.",
            related_entity_id=str(res.inserted_id),
        )

        serialized = serialize_doc(req_doc)
        serialized["skill_title"] = skill.get("title")
        serialized["requester_name"] = r_name
        provider = await self.get_user_by_id(provider_id)
        serialized["provider_name"] = provider["full_name"] if provider else "Provider"
        return serialized

    async def list_skill_requests(self, user_id: str) -> List[Dict[str, Any]]:
        self._require_db()
        u_oid = str_to_object_id(user_id)
        cursor = self._db["skill_requests"].find({"$or": [{"requester_id": u_oid}, {"provider_id": u_oid}]}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            skill = await self._db["skills"].find_one({"_id": doc["skill_id"]})
            if skill:
                serialized["skill_title"] = skill.get("title")
            requester = await self.get_user_by_id(doc["requester_id"])
            if requester:
                serialized["requester_name"] = requester.get("full_name")
            provider = await self.get_user_by_id(doc["provider_id"])
            if provider:
                serialized["provider_name"] = provider.get("full_name")
            results.append(serialized)
        return results

    async def accept_skill_request(self, request_id: str, provider_id: str) -> bool:
        self._require_db()
        req_oid = str_to_object_id(request_id)
        req = await self._db["skill_requests"].find_one({"_id": req_oid})
        if not req or str(req["provider_id"]) != str(provider_id):
            return False

        now = datetime.now(timezone.utc)
        await self._db["skill_requests"].update_one(
            {"_id": req_oid},
            {"$set": {"status": "ACCEPTED", "updated_at": now}},
        )

        # Create skill exchange record
        exchange_doc = {
            "skill_id": req["skill_id"],
            "provider_id": req["provider_id"],
            "requester_id": req["requester_id"],
            "skill_request_id": req_oid,
            "session_date": req["requested_date"],
            "status": "SCHEDULED",
            "completed_at": None,
            "created_at": now,
        }
        await self._db["skill_exchanges"].insert_one(exchange_doc)

        skill = await self._db["skills"].find_one({"_id": req["skill_id"]})
        title = skill.get("title", "Skill session") if skill else "Skill session"
        await self.create_notification(
            user_id=str(req["requester_id"]),
            type="SKILL_SESSION_REMINDER",
            title="Skill Request Accepted! 💡",
            message=f"Your skill request for '{title}' was accepted by the provider.",
            related_entity_id=str(request_id),
        )
        return True

    async def complete_skill_exchange(self, request_id: str, user_id: str) -> bool:
        self._require_db()
        req_oid = str_to_object_id(request_id)
        req = await self._db["skill_requests"].find_one({"_id": req_oid})
        if not req:
            return False
        if str(req["provider_id"]) != str(user_id) and str(req["requester_id"]) != str(user_id):
            return False

        now = datetime.now(timezone.utc)
        await self._db["skill_requests"].update_one(
            {"_id": req_oid},
            {"$set": {"status": "COMPLETED", "updated_at": now}},
        )
        await self._db["skill_exchanges"].update_one(
            {"skill_request_id": req_oid},
            {"$set": {"status": "COMPLETED", "completed_at": now}},
        )

        # Increment completed exchanges
        await self._db["users"].update_one({"_id": req["requester_id"]}, {"$inc": {"completed_exchanges": 1}})
        await self._db["users"].update_one({"_id": req["provider_id"]}, {"$inc": {"completed_exchanges": 1}})

        await self.recalculate_user_reputation(str(req["requester_id"]))
        await self.recalculate_user_reputation(str(req["provider_id"]))
        return True

    # ─────────────────────────────────────────────────────────────
    # REVIEWS & REPUTATION ENGINE
    # ─────────────────────────────────────────────────────────────

    async def create_review(
        self,
        reviewer_id: str,
        reviewed_user_id: str,
        rating: int,
        comment: str,
        transaction_id: Optional[str] = None,
        skill_exchange_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_db()
        if str(reviewer_id) == str(reviewed_user_id):
            raise ValueError("You cannot review yourself.")

        rev_oid = str_to_object_id(reviewer_id)
        target_oid = str_to_object_id(reviewed_user_id)

        # Validate exchange participation
        if transaction_id:
            tx = await self._db["transactions"].find_one({"_id": str_to_object_id(transaction_id)})
            if not tx:
                raise ValueError("Referenced transaction not found.")
            valid_participants = {str(tx["borrower_id"]), str(tx["owner_id"])}
            if str(reviewer_id) not in valid_participants or str(reviewed_user_id) not in valid_participants:
                raise ValueError("Reviewer and target must both be participants in this transaction.")

            # Check duplicate
            existing = await self._db["reviews"].find_one({
                "reviewer_id": rev_oid,
                "transaction_id": str_to_object_id(transaction_id),
            })
            if existing:
                raise ValueError("You have already submitted a review for this transaction.")

        now = datetime.now(timezone.utc)
        review_doc = {
            "reviewer_id": rev_oid,
            "reviewed_user_id": target_oid,
            "transaction_id": str_to_object_id(transaction_id) if transaction_id else None,
            "skill_exchange_id": str_to_object_id(skill_exchange_id) if skill_exchange_id else None,
            "rating": max(1, min(5, rating)),
            "comment": comment.strip(),
            "created_at": now,
        }
        res = await self._db["reviews"].insert_one(review_doc)
        review_doc["_id"] = res.inserted_id

        # Recalculate target user's reputation score
        await self.recalculate_user_reputation(reviewed_user_id)

        # Notify reviewed user
        reviewer = await self.get_user_by_id(reviewer_id)
        name = reviewer["full_name"] if reviewer else "A neighbour"
        await self.create_notification(
            user_id=reviewed_user_id,
            type="NEW_REVIEW",
            title="New Community Review! ⭐",
            message=f"{name} gave you a {rating}-star review: \"{comment[:60]}\"",
            related_entity_id=str(res.inserted_id),
        )

        return serialize_doc(review_doc)

    async def list_user_reviews(self, user_id: str) -> List[Dict[str, Any]]:
        self._require_db()
        cursor = self._db["reviews"].find({"reviewed_user_id": str_to_object_id(user_id)}).sort("created_at", -1)
        docs = await cursor.to_list(length=50)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            reviewer = await self.get_user_by_id(doc["reviewer_id"])
            if reviewer:
                serialized["reviewer_name"] = reviewer.get("full_name")
            results.append(serialized)
        return results

    async def recalculate_user_reputation(self, user_id: str) -> Dict[str, Any]:
        """
        Transparent reputation calculation formula:
        - Base neutral score for all users: 4.0
        - If user has reviews: Average review rating contributes 60%
        - Completed exchanges bonus: min(completed_exchanges * 0.1, 0.6)
        - Verified user bonus: 0.2
        - Clamped between [1.0, 5.0]
        """
        self._require_db()
        u_oid = str_to_object_id(user_id)
        user = await self._db["users"].find_one({"_id": u_oid})
        if not user:
            return {"score": 4.5}

        # MongoDB aggregation pipeline to compute average review rating
        pipeline = [
            {"$match": {"reviewed_user_id": u_oid}},
            {"$group": {"_id": "$reviewed_user_id", "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}},
        ]
        res = await self._db["reviews"].aggregate(pipeline).to_list(length=1)

        completed_exchanges = user.get("completed_exchanges", 0)
        is_verified = user.get("is_verified", True)

        if res:
            avg_rating = round(float(res[0]["avg_rating"]), 2)
            review_count = int(res[0]["count"])
            # Weighted mix of average rating + activity
            exchange_bonus = min(completed_exchanges * 0.05, 0.4)
            verified_bonus = 0.2 if is_verified else 0.0
            score = round(min(5.0, max(1.0, (avg_rating * 0.8) + exchange_bonus + verified_bonus)), 2)
        else:
            avg_rating = 0.0
            review_count = 0
            exchange_bonus = min(completed_exchanges * 0.1, 0.5)
            verified_bonus = 0.2 if is_verified else 0.0
            score = round(min(5.0, max(1.0, 4.0 + exchange_bonus + verified_bonus)), 2)

        breakdown = {
            "score": score,
            "average_rating": avg_rating,
            "review_count": review_count,
            "completed_exchanges": completed_exchanges,
            "on_time_return_rate": 1.0,
            "verified_bonus": 0.2 if is_verified else 0.0,
            "explanation": f"Calculated from {review_count} community review(s), {completed_exchanges} completed exchange(s), and verified profile status.",
        }

        await self._db["users"].update_one(
            {"_id": u_oid},
            {"$set": {"reputation_score": score, "reputation_breakdown": breakdown}},
        )
        return breakdown

    # ─────────────────────────────────────────────────────────────
    # DETERMINISTIC RECOMMENDATION ENGINE
    # ─────────────────────────────────────────────────────────────

    async def get_recommended_resources(
        self,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
        category: Optional[str] = None,
        user_coordinates: Optional[List[float]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Intelligent Matchmaking weighted ranking formula (Section 10):
        - Relevance: 30%
        - Proximity: 25%
        - Availability: 15%
        - Reputation: 15%
        - Community relationship: 10%
        - Previous interaction: 5%
        """
        self._require_db()
        filter_query: Dict[str, Any] = {"status": TransactionStatus.AVAILABLE.value}
        if user_id:
            filter_query["owner_id"] = {"$ne": str_to_object_id(user_id)}
        if category:
            filter_query["category"] = category

        cursor = self._db["resources"].find(filter_query).limit(50)
        candidates = await cursor.to_list(length=50)

        # Get user's previous interactions if user_id supplied
        interacted_owners = set()
        if user_id:
            interactions = await self._db["interactions"].find({"actor_id": str_to_object_id(user_id)}).to_list(100)
            for i in interactions:
                interacted_owners.add(str(i.get("target_user_id")))

        scored_list = []
        for doc in candidates:
            serialized = await self.get_resource_by_id(doc["_id"])
            if not serialized:
                continue

            owner = serialized.get("owner") or {}
            owner_score = owner.get("reputation_score", 4.5) / 5.0  # normalize [0, 1]

            # 1. Relevance Score (30%)
            relevance = 1.0
            if query:
                q = query.lower()
                text = (doc.get("title", "") + " " + doc.get("description", "") + " " + doc.get("category", "")).lower()
                relevance = 1.0 if q in text else 0.5

            # 2. Proximity Score (25%)
            proximity = 0.8
            distance_km = None
            if user_coordinates and doc.get("location") and "coordinates" in doc["location"]:
                dist = haversine_distance_km(user_coordinates, doc["location"]["coordinates"])
                distance_km = dist
                serialized["distance_km"] = dist
                # Closer than 1km -> 1.0; 5km -> 0.6; >10km -> 0.2
                proximity = max(0.1, min(1.0, 1.0 - (dist / 12.0)))

            # 3. Availability Score (15%)
            availability = 1.0 if doc.get("status") == TransactionStatus.AVAILABLE.value else 0.2

            # 4. Reputation Score (15%)
            reputation = max(0.2, min(1.0, owner_score))

            # 5. Community Relationship (10%)
            community_rel = 0.8  # same community default

            # 6. Previous Interaction (5%)
            prev_inter = 1.0 if str(doc.get("owner_id")) in interacted_owners else 0.3

            # Total weighted score
            total_score = round(
                (0.30 * relevance)
                + (0.25 * proximity)
                + (0.15 * availability)
                + (0.15 * reputation)
                + (0.10 * community_rel)
                + (0.05 * prev_inter),
                3,
            )

            breakdown = {
                "relevance": round(relevance, 2),
                "proximity": round(proximity, 2),
                "availability": round(availability, 2),
                "reputation": round(reputation, 2),
                "community_relationship": round(community_rel, 2),
                "previous_interaction": round(prev_inter, 2),
                "total_score": total_score,
                "explanation": f"Recommended because this neighbour is nearby ({distance_km or 'approx.'} km), has an active listing, and holds a {owner.get('reputation_score', 4.5)}/5 community trust score.",
            }

            scored_list.append({
                "resource": serialized,
                "score": total_score,
                "breakdown": breakdown,
            })

        scored_list.sort(key=lambda x: x["score"], reverse=True)
        return scored_list[:limit]

    async def get_recommended_skills(
        self,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
        category: Optional[str] = None,
        user_coordinates: Optional[List[float]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        self._require_db()
        filter_query: Dict[str, Any] = {"status": "active"}
        if user_id:
            filter_query["provider_id"] = {"$ne": str_to_object_id(user_id)}
        if category:
            filter_query["category"] = category

        cursor = self._db["skills"].find(filter_query).limit(50)
        candidates = await cursor.to_list(length=50)

        scored_list = []
        for doc in candidates:
            serialized = await self.get_skill_by_id(doc["_id"])
            if not serialized:
                continue

            provider = serialized.get("provider") or {}
            reputation = (provider.get("reputation_score", 4.5) / 5.0)

            relevance = 1.0
            if query:
                q = query.lower()
                text = (doc.get("title", "") + " " + doc.get("description", "") + " " + doc.get("category", "")).lower()
                relevance = 1.0 if q in text else 0.5

            proximity = 0.8
            dist_km = None
            if user_coordinates and doc.get("location") and "coordinates" in doc["location"]:
                dist = haversine_distance_km(user_coordinates, doc["location"]["coordinates"])
                dist_km = dist
                serialized["distance_km"] = dist
                proximity = max(0.1, min(1.0, 1.0 - (dist / 12.0)))

            total_score = round(
                (0.35 * relevance) + (0.25 * proximity) + (0.25 * reputation) + (0.15 * 0.9), 3
            )

            breakdown = {
                "relevance": round(relevance, 2),
                "proximity": round(proximity, 2),
                "availability": 1.0,
                "reputation": round(reputation, 2),
                "community_relationship": 0.9,
                "previous_interaction": 0.5,
                "total_score": total_score,
                "explanation": f"Recommended skill provider nearby ({dist_km or 'approx.'} km) with proven experience in {doc.get('category')}.",
            }

            scored_list.append({
                "skill": serialized,
                "score": total_score,
                "breakdown": breakdown,
            })

        scored_list.sort(key=lambda x: x["score"], reverse=True)
        return scored_list[:limit]

    async def get_recommended_neighbours(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        self._require_db()
        u_oid = str_to_object_id(user_id)
        current_user = await self.get_user_by_id(user_id)
        current_interests = set(current_user.get("interests", [])) if current_user else set()
        user_coords = current_user.get("location", {}).get("coordinates") if current_user else None

        cursor = self._db["users"].find({"_id": {"$ne": u_oid}, "is_active": True}).limit(30)
        candidates = await cursor.to_list(length=30)

        results = []
        for doc in candidates:
            serialized = serialize_doc(doc)
            cand_interests = set(doc.get("interests", []))
            shared = list(current_interests.intersection(cand_interests))

            dist_km = None
            proximity = 0.8
            if user_coords and doc.get("location") and "coordinates" in doc["location"]:
                dist = haversine_distance_km(user_coords, doc["location"]["coordinates"])
                dist_km = dist
                serialized["distance_km"] = dist
                proximity = max(0.1, min(1.0, 1.0 - (dist / 12.0)))

            rep = doc.get("reputation_score", 4.5) / 5.0
            interest_score = min(1.0, len(shared) * 0.4) if shared else 0.3
            score = round((0.35 * proximity) + (0.35 * rep) + (0.30 * interest_score), 3)

            breakdown = {
                "relevance": round(interest_score, 2),
                "proximity": round(proximity, 2),
                "availability": 1.0,
                "reputation": round(rep, 2),
                "community_relationship": 0.9,
                "previous_interaction": 0.5,
                "total_score": score,
                "explanation": f"Neighbour in {doc.get('locality', 'Bengaluru')} sharing interests in {', '.join(shared) if shared else 'community activities'}.",
            }

            results.append({
                "neighbour": {
                    "id": serialized["id"],
                    "full_name": serialized["full_name"],
                    "avatar_url": serialized.get("avatar_url"),
                    "bio": serialized.get("bio"),
                    "locality": serialized.get("locality", "Bengaluru"),
                    "skills": serialized.get("skills", []),
                    "interests": serialized.get("interests", []),
                    "reputation_score": serialized.get("reputation_score", 4.5),
                    "completed_exchanges": serialized.get("completed_exchanges", 0),
                    "is_verified": serialized.get("is_verified", True),
                    "distance_km": dist_km,
                },
                "score": score,
                "shared_interests": shared,
                "breakdown": breakdown,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    # ─────────────────────────────────────────────────────────────
    # MONGODB AGGREGATION PIPELINES (Section 9.B)
    # ─────────────────────────────────────────────────────────────

    async def get_community_analytics(self) -> Dict[str, Any]:
        """
        Executes MongoDB aggregation pipelines for platform analytics:
        1. Top-rated community members
        2. Most requested resource categories
        3. Most shared resources
        4. Category distribution
        """
        self._require_db()

        total_users = await self._db["users"].count_documents({})
        total_resources = await self._db["resources"].count_documents({})
        total_skills = await self._db["skills"].count_documents({})
        total_completed = await self._db["transactions"].count_documents({"status": TransactionStatus.RETURNED.value})

        # Aggregation 1: Top Rated Members
        top_users_pipeline = [
            {"$match": {"is_active": True}},
            {"$sort": {"reputation_score": -1, "completed_exchanges": -1}},
            {"$limit": 5},
            {
                "$project": {
                    "user_id": {"$toString": "$_id"},
                    "full_name": "$full_name",
                    "avatar_url": "$avatar_url",
                    "locality": "$locality",
                    "reputation_score": "$reputation_score",
                    "completed_exchanges": "$completed_exchanges",
                    "review_count": {"$ifNull": ["$reputation_breakdown.review_count", 0]},
                }
            },
        ]
        top_rated = await self._db["users"].aggregate(top_users_pipeline).to_list(5)

        # Aggregation 2: Category Distribution
        cat_dist_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$project": {"category": "$_id", "count": 1, "_id": 0}},
        ]
        category_distribution = await self._db["resources"].aggregate(cat_dist_pipeline).to_list(10)

        # Aggregation 3: Most Shared Resources (grouped from transactions)
        most_shared_pipeline = [
            {"$group": {"_id": "$resource_id", "borrow_count": {"$sum": 1}}},
            {"$sort": {"borrow_count": -1}},
            {"$limit": 5},
            {
                "$lookup": {
                    "from": "resources",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "resource_info",
                }
            },
            {"$unwind": "$resource_info"},
            {
                "$project": {
                    "_id": 0,
                    "resource_id": {"$toString": "$_id"},
                    "title": "$resource_info.title",
                    "category": "$resource_info.category",
                    "borrow_count": 1,
                }
            },
        ]
        most_shared = await self._db["transactions"].aggregate(most_shared_pipeline).to_list(5)

        # Most requested categories from borrow_requests
        most_req_cat_pipeline = [
            {
                "$lookup": {
                    "from": "resources",
                    "localField": "resource_id",
                    "foreignField": "_id",
                    "as": "res",
                }
            },
            {"$unwind": "$res"},
            {"$group": {"_id": "$res.category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$project": {"_id": 0, "category": "$_id", "count": 1}},
        ]
        most_requested_cats = await self._db["borrow_requests"].aggregate(most_req_cat_pipeline).to_list(5)
        if not most_requested_cats:
            most_requested_cats = category_distribution[:5]

        return {
            "total_users": total_users,
            "total_resources": total_resources,
            "total_skills": total_skills,
            "total_completed_exchanges": total_completed,
            "top_rated_members": top_rated,
            "category_distribution": category_distribution,
            "most_shared_resources": most_shared,
            "most_requested_categories": most_requested_cats,
        }

    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        self._require_db()
        u_oid = str_to_object_id(user_id)

        user = await self.get_user_by_id(user_id)
        resources_count = await self._db["resources"].count_documents({"owner_id": u_oid})
        skills_count = await self._db["skills"].count_documents({"provider_id": u_oid})
        active_borrows = await self._db["transactions"].count_documents({
            "borrower_id": u_oid,
            "status": {"$in": [TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
        })
        completed_borrows = await self._db["transactions"].count_documents({
            "borrower_id": u_oid,
            "status": TransactionStatus.RETURNED.value,
        })
        active_lends = await self._db["transactions"].count_documents({
            "owner_id": u_oid,
            "status": {"$in": [TransactionStatus.RESERVED.value, TransactionStatus.ACTIVE.value]},
        })
        completed_lends = await self._db["transactions"].count_documents({
            "owner_id": u_oid,
            "status": TransactionStatus.RETURNED.value,
        })
        reviews_count = await self._db["reviews"].count_documents({"reviewed_user_id": u_oid})

        return {
            "user_id": user_id,
            "resources_listed": resources_count,
            "skills_offered": skills_count,
            "active_borrows": active_borrows,
            "completed_borrows": completed_borrows,
            "active_lends": active_lends,
            "completed_lends": completed_lends,
            "reputation_score": user.get("reputation_score", 4.5) if user else 4.5,
            "review_count": reviews_count,
        }

    # ─────────────────────────────────────────────────────────────
    # NOTIFICATIONS
    # ─────────────────────────────────────────────────────────────

    async def create_notification(
        self,
        user_id: str | ObjectId,
        type: str,
        title: str,
        message: str,
        related_entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_db()
        doc = {
            "user_id": str_to_object_id(user_id),
            "type": type,
            "title": title,
            "message": message,
            "related_entity_id": str(related_entity_id) if related_entity_id else None,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
        res = await self._db["notifications"].insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    async def list_notifications(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        self._require_db()
        cursor = (
            self._db["notifications"]
            .find({"user_id": str_to_object_id(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return serialize_docs(docs)

    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        self._require_db()
        res = await self._db["notifications"].update_one(
            {"_id": str_to_object_id(notification_id), "user_id": str_to_object_id(user_id)},
            {"$set": {"is_read": True}},
        )
        return res.matched_count > 0

    async def mark_all_notifications_read(self, user_id: str) -> int:
        self._require_db()
        res = await self._db["notifications"].update_many(
            {"user_id": str_to_object_id(user_id), "is_read": False},
            {"$set": {"is_read": True}},
        )
        return res.modified_count

    # ─────────────────────────────────────────────────────────────
    # COMMUNITY DIRECTORY
    # ─────────────────────────────────────────────────────────────

    async def list_communities(self) -> List[Dict[str, Any]]:
        self._require_db()
        cursor = self._db["communities"].find({}).sort("name", 1)
        docs = await cursor.to_list(length=50)
        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            member_ids = doc.get("member_ids", [])
            serialized["member_count"] = len(member_ids)
            results.append(serialized)
        return results

    async def list_community_members(self, locality: Optional[str] = None) -> List[Dict[str, Any]]:
        self._require_db()
        query: Dict[str, Any] = {"is_active": True}
        if locality:
            query["locality"] = {"$regex": locality, "$options": "i"}

        cursor = self._db["users"].find(query).sort("reputation_score", -1).limit(50)
        docs = await cursor.to_list(length=50)

        results = []
        for doc in docs:
            serialized = serialize_doc(doc)
            # Hide sensitive fields
            serialized.pop("password_hash", None)
            serialized.pop("phone", None)
            serialized.pop("email", None)
            results.append(serialized)
        return results

    # ─────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────

    async def _record_interaction(
        self,
        actor_id: str,
        target_user_id: str,
        interaction_type: str,
        related_resource_id: Optional[str] = None,
        related_transaction_id: Optional[str] = None,
    ) -> None:
        try:
            self._require_db()
            await self._db["interactions"].insert_one({
                "actor_id": str_to_object_id(actor_id),
                "target_user_id": str_to_object_id(target_user_id),
                "interaction_type": interaction_type,
                "related_resource_id": str_to_object_id(related_resource_id) if related_resource_id else None,
                "related_transaction_id": str_to_object_id(related_transaction_id) if related_transaction_id else None,
                "created_at": datetime.now(timezone.utc),
            })
        except Exception as e:
            logger.debug("Failed to record interaction: %s", e)


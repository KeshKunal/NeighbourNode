"""
SupabaseService — merged from Member 2 (typed) and Member 3 (CRUD).

Single class that owns ALL database interactions.
Uses TransactionStatus from schemas.transaction (the 7-value canonical enum).
"""
from __future__ import annotations

import logging
from typing import Any

from app.schemas.telegram import OverdueReminderMessage
from app.schemas.transaction import TransactionStatus, TransactionUpdateResult


logger = logging.getLogger(__name__)


class SupabaseService:
    def __init__(self, db_client: Any | None = None) -> None:
        self._db = db_client

    def _has_client(self) -> bool:
        if self._db is None:
            logger.warning("supabase.client.missing")
            return False
        return True

    # ─── CRUD: Items ─────────────────────────────────────────────

    def get_items(self, status: str | None = None) -> list[dict]:
        if not self._has_client():
            return []
        query = self._db.table("items").select("*")
        if status:
            query = query.eq("current_status", status)
        return query.execute().data or []

    def create_item(self, item_data: dict) -> list[dict]:
        if not self._has_client():
            return []
        return self._db.table("items").insert(item_data).execute().data or []

    # ─── CRUD: Users ─────────────────────────────────────────────

    def get_user_by_telegram_id(self, chat_id: str) -> list[dict]:
        if not self._has_client():
            return []
        return (
            self._db.table("users")
            .select("*")
            .eq("telegram_chat_id", chat_id)
            .execute()
            .data or []
        )

    def get_user_by_id(self, user_id: str) -> dict | None:
        if not self._has_client():
            return None
        data = (
            self._db.table("users")
            .select("*")
            .eq("id", user_id)
            .execute()
            .data
        )
        return data[0] if data else None

    def create_user(self, user_data: dict) -> list[dict]:
        if not self._has_client():
            return []
        return self._db.table("users").insert(user_data).execute().data or []

    def update_user_profile(self, user_id: str, profile_data: dict) -> dict | None:
        if not self._has_client():
            return None
        try:
            profile_data["id"] = user_id
            response = (
                self._db.table("users")
                .upsert(profile_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception:
            logger.exception("supabase.update_user.failed")
            return None

    # ─── CRUD: Items (single) ────────────────────────────────────

    def get_item(self, item_id: str) -> dict | None:
        """Fetch a single item by ID. Used by the portal-first orchestrator."""
        if not self._has_client():
            return None
        data = (
            self._db.table("items")
            .select("*")
            .eq("id", item_id)
            .execute()
            .data
        )
        return data[0] if data else None

    # ─── CRUD: Transactions ──────────────────────────────────────

    def create_transaction(self, tx_data: dict) -> list[dict]:
        if not self._has_client():
            return []
        return self._db.table("transactions").insert(tx_data).execute().data or []

    def get_transaction(self, tx_id: str) -> dict | None:
        if not self._has_client():
            return None
        data = (
            self._db.table("transactions")
            .select("*")
            .eq("id", tx_id)
            .execute()
            .data
        )
        return data[0] if data else None

    def update_status(self, transaction_id: str, status: TransactionStatus) -> dict | None:
        """
        Advance a transaction through the lifecycle:
        pending_approval → reserved → active → returned / cancelled.
        Returns the updated row or None on failure.
        """
        if not self._has_client():
            return None
        try:
            response = (
                self._db.table("transactions")
                .update({"status": status.value})
                .eq("id", transaction_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception:
            logger.exception("supabase.update_status.failed")
            return None

    # ─── Matchmaker: Real Inventory Search ───────────────────────

    def search_items_by_name(self, item_name: str) -> list[dict]:
        """
        Synchronous search used by the Matchmaker ADK tool.

        Finds available items whose `name` matches the query (ILIKE),
        joined with their owner info, sorted by owner rating descending.
        Returns up to 5 matches.
        """
        if not self._has_client():
            return []
        try:
            response = (
                self._db.table("items")
                .select(
                    "id, title, description, "
                    "owner_id, users(id, full_name, telegram_chat_id, building_identifier, rating)"
                )
                .ilike("title", f"%{item_name}%")
                .eq("current_status", TransactionStatus.AVAILABLE.value)
                .eq("is_active", True)
                .limit(5)
                .execute()
            )
            return response.data or []
        except Exception:
            logger.exception("supabase.search_items.failed")
            return []

    # ─── Transaction Lifecycle ───────────────────────────────────

    async def get_transaction_item_id(self, transaction_id: str) -> str | None:
        if not self._has_client():
            return None
        try:
            response = (
                self._db.table("transactions")
                .select("item_id")
                .eq("id", transaction_id)
                .execute()
            )
            if response.data:
                return response.data[0].get("item_id")
        except Exception:
            logger.exception("supabase.transaction.lookup.failed")
        return None

    async def get_transaction_full(self, transaction_id: str) -> dict | None:
        """
        Fetch full transaction with joined item + borrower + owner details.
        Used by the Telegram APPROVE handler to build CalendarEventRequest.
        """
        if not self._has_client():
            return None
        try:
            response = (
                self._db.table("transactions")
                .select(
                    "*, "
                    "items(title, users(full_name, email, telegram_chat_id)), "
                    "borrower:users!borrower_id(full_name, email, telegram_chat_id)"
                )
                .eq("id", transaction_id)
                .execute()
            )
            if response.data:
                return response.data[0]
        except Exception:
            logger.exception("supabase.transaction.full.lookup.failed")
        return None

    async def approve_transaction(
        self,
        transaction_id: str,
        item_id: str,
    ) -> TransactionUpdateResult:
        """
        Called when owner taps [ ✅ Approve ] on Telegram.
        Updates BOTH the transaction ledger and the item catalog.
        """
        if not self._has_client():
            return TransactionUpdateResult(
                success=False,
                message="Supabase client not configured",
                transaction_id=transaction_id,
                item_id=item_id,
            )

        try:
            # 1. Update the Transaction Ledger
            tx_response = (
                self._db.table("transactions")
                .update({"status": TransactionStatus.RESERVED.value})
                .eq("id", transaction_id)
                .execute()
            )
            if not tx_response.data:
                return TransactionUpdateResult(
                    success=False,
                    message="Transaction update failed",
                    transaction_id=transaction_id,
                    item_id=item_id,
                )

            # 2. Update the Item Catalog
            item_response = (
                self._db.table("items")
                .update({"current_status": TransactionStatus.RESERVED.value})
                .eq("id", item_id)
                .execute()
            )
            if not item_response.data:
                return TransactionUpdateResult(
                    success=False,
                    message="Item status update failed",
                    transaction_id=transaction_id,
                    item_id=item_id,
                )

            return TransactionUpdateResult(
                success=True,
                message="Transaction and item marked RESERVED",
                transaction_id=transaction_id,
                item_id=item_id,
            )
        except Exception:
            logger.exception("supabase.transaction.approve.failed")
            return TransactionUpdateResult(
                success=False,
                message="Supabase update failed",
                transaction_id=transaction_id,
                item_id=item_id,
            )

    async def update_transaction_calendar(
        self,
        transaction_id: str,
        calendar_event_id: str,
    ) -> bool:
        """Store the Google Calendar event ID on the transaction row."""
        if not self._has_client():
            return False
        try:
            response = (
                self._db.table("transactions")
                .update({"calendar_event_id": calendar_event_id})
                .eq("id", transaction_id)
                .execute()
            )
            return bool(response.data)
        except Exception:
            logger.exception("supabase.transaction.calendar.update.failed")
            return False

    # ─── Warden: Overdue Detection ───────────────────────────────

    async def fetch_overdue_transactions(self) -> list[OverdueReminderMessage]:
        """
        Find transactions past their requested_end that are still RESERVED.
        Joins borrower info for Telegram notifications.
        """
        if not self._has_client():
            return []
        try:
            response = (
                self._db.table("transactions")
                .select(
                    "id, item_id, borrower_id, requested_end, "
                    "items(title), "
                    "borrower:users!borrower_id(telegram_chat_id)"
                )
                .eq("status", TransactionStatus.RESERVED.value)
                .lt("requested_end", "now()")
                .execute()
            )
            reminders: list[OverdueReminderMessage] = []
            for row in response.data or []:
                borrower = row.get("borrower") or {}
                borrower_chat_id = borrower.get("telegram_chat_id")
                if not borrower_chat_id:
                    continue
                item_info = row.get("items") or {}
                reminders.append(
                    OverdueReminderMessage(
                        transaction_id=row.get("id"),
                        borrower_chat_id=int(borrower_chat_id),
                        item_name=item_info.get("title", ""),
                        overdue_since=row.get("requested_end"),
                    )
                )
            return reminders
        except Exception:
            logger.exception("supabase.overdue.fetch.failed")
            return []

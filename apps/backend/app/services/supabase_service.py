<<<<<<< HEAD
from supabase import Client
from app.schemas.transaction import TransactionStatus

class SupabaseService:
    def __init__(self, db_client: Client):
        self.db = db_client

    async def approve_transaction(self, transaction_id: str, item_id: str) -> dict:
        """
        Called when a user taps [ ✅ Approve ] on Telegram.
        Updates BOTH the transaction ledger and the item catalog to prevent double-booking.
        """
        # 1. Update the Transaction Ledger
        tx_response = self.db.table("transactions").update({
            "status": TransactionStatus.RESERVED.value
        }).eq("id", transaction_id).execute()
        
        if not tx_response.data:
            raise ValueError("Transaction update failed.")
            
        # 2. Update the Item Catalog
        item_response = self.db.table("items").update({
            "current_status": TransactionStatus.RESERVED.value
        }).eq("id", item_id).execute()
        
        if not item_response.data:
            raise ValueError("Item status update failed.")
            
        return {"success": True, "message": "Transaction and Item marked RESERVED."}

    def get_items(self, status: str = None):
        query = self.db.table("items").select("*")
        if status:
            query = query.eq("current_status", status)
        return query.execute().data

    def create_item(self, item_data: dict):
        return self.db.table("items").insert(item_data).execute().data

    def get_user_by_telegram_id(self, chat_id: str):
        return self.db.table("users").select("*").eq("telegram_chat_id", chat_id).execute().data

    def create_user(self, user_data: dict):
        return self.db.table("users").insert(user_data).execute().data

    def create_transaction(self, tx_data: dict):
        return self.db.table("transactions").insert(tx_data).execute().data
        
    def get_transaction(self, tx_id: str):
        return self.db.table("transactions").select("*").eq("id", tx_id).execute().data
=======
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

	async def approve_transaction(
		self,
		transaction_id: str,
		item_id: str,
	) -> TransactionUpdateResult:
		if not self._has_client():
			return TransactionUpdateResult(
				success=False,
				message="Supabase client not configured",
				transaction_id=transaction_id,
				item_id=item_id,
			)

		try:
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

	async def fetch_overdue_transactions(self) -> list[OverdueReminderMessage]:
		if not self._has_client():
			return []
		try:
			response = (
				self._db.table("transactions")
				.select("id,item_id,borrower_id,requested_end,users(telegram_chat_id)")
				.eq("status", TransactionStatus.RESERVED.value)
				.lt("requested_end", "now()")
				.execute()
			)
			items: list[OverdueReminderMessage] = []
			for row in response.data or []:
				borrower_chat_id = row.get("users", {}).get("telegram_chat_id")
				if not borrower_chat_id:
					continue
				items.append(
					OverdueReminderMessage(
						transaction_id=row.get("id"),
						borrower_chat_id=int(borrower_chat_id),
						item_name="",
						overdue_since=row.get("requested_end"),
					)
				)
			return items
		except Exception:
			logger.exception("supabase.overdue.fetch.failed")
			return []
>>>>>>> 9923707 (Implement Telegram integration with calendar and notification services)

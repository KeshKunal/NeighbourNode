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

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.api import BorrowRequest, BorrowResponse
from app.services.supabase_service import SupabaseService
from app.api.dependencies import get_supabase_service

router = APIRouter(prefix="/borrow", tags=["borrow"])

@router.post("/", response_model=BorrowResponse)
async def create_borrow_request(payload: BorrowRequest, supabase: SupabaseService = Depends(get_supabase_service)):
    try:
        # 1. Verify item exists and is available
        items = supabase.db.table("items").select("*").eq("id", payload.item_id).execute().data
        if not items:
            raise HTTPException(status_code=404, detail="Item not found")
            
        item = items[0]
        if item.get("current_status") != "available":
            raise HTTPException(status_code=400, detail="Item is not available")
            
        # 2. Insert transaction
        tx_data = {
            "item_id": payload.item_id,
            "borrower_id": payload.borrower_id,
            "owner_id": item["owner_id"],
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "status": "pending_approval"
        }
        
        tx_res = supabase.create_transaction(tx_data)
        if not tx_res:
            raise HTTPException(status_code=500, detail="Failed to create transaction")
            
        # Note: Matchmaker/Telegram logic will be triggered here or separately by the orchestrator.
            
        return BorrowResponse(
            success=True, 
            transaction_id=tx_res[0]["id"], 
            message="Borrow request created. Waiting for owner approval."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

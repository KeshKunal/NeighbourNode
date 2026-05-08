"""
Borrow route — direct borrow by item_id (frontend catalog flow).

For agent-driven borrow by item_name, use /api/orchestrate/borrow instead.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.api import BorrowRequest, BorrowResponse
from app.schemas.transaction import TransactionStatus
from app.services.supabase_service import SupabaseService
from app.api.dependencies import get_supabase_service


router = APIRouter(prefix="/borrow", tags=["borrow"])


@router.post("/", response_model=BorrowResponse)
async def create_borrow_request(
    payload: BorrowRequest,
    supabase: SupabaseService = Depends(get_supabase_service),
) -> BorrowResponse:
    try:
        # 1. Verify item exists and is available
        items = supabase.get_items()
        item = next(
            (i for i in items if i.get("id") == payload.item_id),
            None,
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        if item.get("current_status") != TransactionStatus.AVAILABLE.value:
            raise HTTPException(status_code=400, detail="Item is not available")

        # 2. Insert transaction
        tx_data = {
            "item_id": payload.item_id,
            "borrower_id": payload.borrower_id,
            "owner_id": item["owner_id"],
            "requested_start": payload.requested_start.isoformat(),
            "requested_end": payload.requested_end.isoformat(),
            "status": TransactionStatus.PENDING_APPROVAL.value,
        }

        tx_res = supabase.create_transaction(tx_data)
        if not tx_res:
            raise HTTPException(status_code=500, detail="Failed to create transaction")

        # Note: Matchmaker/Telegram logic is triggered via /api/orchestrate/borrow
        return BorrowResponse(
            success=True,
            transaction_id=tx_res[0]["id"],
            message="Borrow request created. Waiting for owner approval.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

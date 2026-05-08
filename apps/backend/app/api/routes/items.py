from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.supabase_service import SupabaseService
from app.api.dependencies import get_supabase_service

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemResponse])
async def list_items(status: Optional[str] = None, supabase: SupabaseService = Depends(get_supabase_service)):
    try:
        items = supabase.get_items(status)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, supabase: SupabaseService = Depends(get_supabase_service)):
    try:
        data = supabase.create_item(item.model_dump())
        if not data:
            raise HTTPException(status_code=400, detail="Failed to create item")
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.users import UserCreate, UserResponse
from app.services.supabase_service import SupabaseService
from app.api.dependencies import get_supabase_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, supabase: SupabaseService = Depends(get_supabase_service)):
    try:
        data = supabase.create_user(user.model_dump(exclude_unset=True))
        if not data:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/{chat_id}", response_model=UserResponse)
async def get_user_by_telegram(chat_id: str, supabase: SupabaseService = Depends(get_supabase_service)):
    try:
        data = supabase.get_user_by_telegram_id(chat_id)
        if not data:
            raise HTTPException(status_code=404, detail="User not found")
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

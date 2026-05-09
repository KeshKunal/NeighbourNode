from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    building: Optional[str] = None

class UserResponse(UserBase):
    id: str
    rating: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

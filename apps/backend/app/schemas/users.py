from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    rating: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

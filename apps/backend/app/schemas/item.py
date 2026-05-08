from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .transaction import TransactionStatus

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    location_hint: Optional[str] = None
    is_active: bool = True
    current_status: TransactionStatus = TransactionStatus.AVAILABLE

class ItemCreate(ItemBase):
    owner_id: str

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    location_hint: Optional[str] = None
    is_active: Optional[bool] = None
    current_status: Optional[TransactionStatus] = None

class ItemResponse(ItemBase):
    id: str
    owner_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

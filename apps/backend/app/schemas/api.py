from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class BorrowRequest(BaseModel):
    item_id: str
    borrower_id: str
    requested_start: datetime
    requested_end: datetime

class BorrowResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: str

class MatchResult(BaseModel):
    success: bool
    owner_id: Optional[str] = None
    item_id: Optional[str] = None
    proposed_time: Optional[str] = None
    
class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

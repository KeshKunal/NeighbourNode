"""
Borrowing and Transactions routes for NeighbourNode (/api/v1/borrow-requests).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_mongodb_service, get_optional_current_user
from app.schemas.api import BorrowRequest, BorrowResponse
from app.schemas.borrow import BorrowRequestCreate, BorrowRequestResponse, TransactionResponse
from app.schemas.transaction import TransactionUpdateResult
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/borrow-requests", tags=["borrowing"])


@router.post("", response_model=BorrowRequestResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BorrowRequestResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_borrow_request(
    payload: BorrowRequestCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> BorrowRequestResponse:
    try:
        req = await mongodb_svc.create_borrow_request(
            resource_id=payload.resource_id,
            borrower_id=current_user["id"],
            requested_start=payload.requested_start,
            requested_end=payload.requested_end,
            message=payload.message,
        )
        return BorrowRequestResponse(**req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Failed to create borrow request: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[BorrowRequestResponse])
@router.get("/", response_model=List[BorrowRequestResponse], include_in_schema=False)
async def list_borrow_requests(
    role: str = Query("all", description="borrower | owner | all"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> List[BorrowRequestResponse]:
    requests = await mongodb_svc.list_borrow_requests(user_id=current_user["id"], role=role)
    return [BorrowRequestResponse(**r) for r in requests]


@router.post("/{request_id}/approve", response_model=TransactionUpdateResult)
async def approve_borrow_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> TransactionUpdateResult:
    result = await mongodb_svc.approve_borrow_request(request_id=request_id, owner_id=current_user["id"])
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/{request_id}/reject")
async def reject_borrow_request(
    request_id: str,
    reason: Optional[str] = Query(""),
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    success = await mongodb_svc.reject_borrow_request(request_id=request_id, owner_id=current_user["id"], reason=reason or "")
    if not success:
        raise HTTPException(status_code=400, detail="Unable to reject borrow request")
    return {"message": "Borrow request rejected"}


@router.post("/{request_id}/start")
async def start_loan(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    success = await mongodb_svc.start_transaction(request_id=request_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Unable to mark loan as active")
    return {"message": "Loan is now active"}


@router.post("/{request_id}/return")
async def return_loan(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> Dict[str, str]:
    success = await mongodb_svc.return_transaction(request_id=request_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Unable to confirm return")
    return {"message": "Resource returned successfully and marked available"}

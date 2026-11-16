"""
Authentication routes for NeighbourNode (/api/v1/auth).
"""
from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_mongodb_service
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.users import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: UserRegister,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> TokenResponse:
    existing = await mongodb_svc.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    user_dict = payload.model_dump()
    user_dict["password_hash"] = hash_password(user_dict.pop("password"))

    # Default GeoJSON location in Bengaluru (Ramaiah Institute / Mathikere) if not specified
    if not user_dict.get("location"):
        user_dict["location"] = {
            "type": "Point",
            "coordinates": [77.5649, 13.0308],  # [lon, lat] MSRIT, Bengaluru
        }

    created_user = await mongodb_svc.create_user(user_dict)
    token = create_access_token({"sub": created_user["id"], "email": created_user["email"]})
    return TokenResponse(access_token=token, user=UserResponse(**created_user))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    mongodb_svc: MongoDBService = Depends(get_mongodb_service),
) -> TokenResponse:
    user = await mongodb_svc.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = await mongodb_svc.get_user_by_id(user["_id"])
    token = create_access_token({"sub": user_data["id"], "email": user_data["email"]})
    return TokenResponse(access_token=token, user=UserResponse(**user_data))


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(**current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> TokenResponse:
    token = create_access_token({"sub": current_user["id"], "email": current_user["email"]})
    return TokenResponse(access_token=token, user=UserResponse(**current_user))


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    return {"message": "Logged out successfully"}


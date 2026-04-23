"""
auth_routes.py — /api/v1/auth/{register,login,me} для JWT-аутентификации.

Подключается в main.py:
    app.include_router(auth_router, prefix="/api/v1")
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database import crud
from database.models import User as UserDB
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)


auth_router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Pydantic schemas ────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class RegisterResponse(BaseModel):
    id: int
    email: str
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: Optional[str] = None
    name: Optional[str] = None


# ─── Endpoints ───────────────────────────────────────────────────────────────

@auth_router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_data = {
        "name": payload.name or payload.email.split("@")[0],
        "role": "founder",
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "is_active": True,
    }
    user = await crud.create_user(db, user_data)
    token = create_access_token({"sub": user.email, "uid": user.id})
    return RegisterResponse(id=user.id, email=user.email, token=token)


@auth_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    user = await crud.get_user_by_email(db, payload.email)
    if user is None:
        raise unauthorized
    if not verify_password(payload.password, user.hashed_password or ""):
        raise unauthorized
    token = create_access_token({"sub": user.email, "uid": user.id})
    return LoginResponse(token=token, token_type="bearer")


@auth_router.get("/me", response_model=MeResponse)
async def me(current: UserDB = Depends(get_current_user)):
    return MeResponse(id=current.id, email=current.email, name=current.name)

"""
profile_routes.py — GET/PATCH /api/v1/profile/me (C6).

Профиль текущего пользователя: данные из users + founder_profiles.normalized_profile.
Подключается в main.py:
    app.include_router(profile_router, prefix="/api/v1")
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database import crud
from database.models import User as UserDB
from auth import get_current_user


profile_router = APIRouter(prefix="/profile", tags=["profile"])


# ─── Pydantic schemas ────────────────────────────────────────────────────────

class ProfilePatchRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    primary_role: Optional[str] = None
    intent_goal: Optional[str] = None


class ProfileResponse(BaseModel):
    id: Optional[str] = None          # founder_profiles.id (UUID); None если ещё нет
    user_id: int
    email: Optional[str] = None
    name: Optional[str] = None
    primary_role: Optional[str] = None
    bio: Optional[str] = None
    stack: Optional[Any] = None
    goals: Optional[Any] = None
    intent_goal: Optional[str] = None
    risk_flags: Optional[Any] = None
    mbti_type: Optional[str] = None
    created_at: Optional[str] = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_response(user: UserDB, profile) -> ProfileResponse:
    """Формирует ProfileResponse из UserDB + (optional) FounderProfileDB."""
    if profile is None:
        return ProfileResponse(
            id=None,
            user_id=user.id,
            email=user.email,
            name=user.name,
            primary_role=str(user.role) if user.role else None,
        )

    np: Dict[str, Any] = profile.normalized_profile or {}
    ra: Dict[str, Any] = profile.raw_answers or {}

    primary_role = np.get("primary_role")
    if primary_role is not None:
        primary_role = str(primary_role)

    intent_goal = np.get("intent_goal")
    if intent_goal is not None:
        intent_goal = str(intent_goal)

    created_at = profile.created_at.isoformat() if profile.created_at else None

    return ProfileResponse(
        id=profile.id,
        user_id=user.id,
        email=user.email,
        name=user.name,
        primary_role=primary_role,
        bio=np.get("bio") or ra.get("bio"),
        stack=np.get("stack") or ra.get("stack"),
        goals=np.get("goals") or ra.get("goals"),
        intent_goal=intent_goal,
        risk_flags=np.get("risk_flags") or ra.get("risk_flags"),
        mbti_type=np.get("mbti_type") or ra.get("mbti_type"),
        created_at=created_at,
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@profile_router.get("/me", response_model=ProfileResponse)
async def get_me(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await crud.get_founder_profile_by_user_id(db, current_user.id)
    return _build_response(current_user, profile)


@profile_router.patch("/me", response_model=ProfileResponse)
async def patch_me(
    payload: ProfilePatchRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)

    # name обновляем на users
    if "name" in updates:
        await crud.update_user(db, current_user.id, {"name": updates["name"]})
        await db.refresh(current_user)

    # остальные поля — в founder_profiles.normalized_profile
    profile_updates = {k: v for k, v in updates.items() if k != "name"}
    if profile_updates:
        profile = await crud.update_founder_profile(db, current_user.id, profile_updates)
    else:
        profile = await crud.get_founder_profile_by_user_id(db, current_user.id)

    return _build_response(current_user, profile)

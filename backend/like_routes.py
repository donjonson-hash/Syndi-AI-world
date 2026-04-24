"""
like_routes.py — эндпоинты для like/match механики (Tinder-свайп).

Добавляется в main.py как отдельный router:
  app.include_router(like_router, prefix="/api/v1")

Endpoints:
  POST /api/v1/like/{to_user_id}   — поставить лайк/дизлайк
  GET  /api/v1/matches             — список взаимных матчей текущего пользователя
"""
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database import crud
from database.models import User as UserDB
from auth import get_current_user
from scoring import score_pair, FounderProfile
from avatar_platform.avatar_factory import AvatarFactory

logger = logging.getLogger(__name__)

like_router = APIRouter(tags=["likes"])


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class LikeRequest(BaseModel):
    from_user_id: int
    is_like: bool = True   # True = like, False = dislike


class LikeResponse(BaseModel):
    like_id: str
    from_user_id: int
    to_user_id: int
    is_like: bool
    is_match: bool          # True — взаимный лайк, матч создан
    match_id: Optional[str] = None
    match_score: Optional[float] = None


class MatchCard(BaseModel):
    match_id: str
    partner_user_id: int
    partner_name: str
    match_score: Optional[float]
    status: str


class MatchesResponse(BaseModel):
    user_id: int
    matches: list[MatchCard]
    total: int


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _founder_profile_from_db(fp_db) -> Optional[FounderProfile]:
    """Восстанавливает FounderProfile из JSON stored в normalized_profile."""
    if not fp_db:
        return None
    try:
        return FounderProfile(**fp_db.normalized_profile)
    except Exception:
        return None


async def _compute_match_score(
    db: AsyncSession,
    user_a_id: int,
    user_b_id: int,
) -> Optional[float]:
    """Считает FounderFit score между двумя пользователями если у обоих есть founder_profiles."""
    fp_a = await crud.get_founder_profile_by_user_id(db, user_a_id)
    fp_b = await crud.get_founder_profile_by_user_id(db, user_b_id)
    if not fp_a or not fp_b:
        return None
    profile_a = _founder_profile_from_db(fp_a)
    profile_b = _founder_profile_from_db(fp_b)
    if not profile_a or not profile_b:
        return None
    try:
        result = score_pair(profile_a, profile_b)
        return round(result.total_compatibility_score, 2)
    except Exception:
        return None


# ─── Endpoints ───────────────────────────────────────────────────────────────

@like_router.post("/like/{to_user_id}", response_model=LikeResponse)
async def post_like(
    to_user_id: int,
    body: LikeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Поставить лайк (is_like=true) или дизлайк (is_like=false).

    Body: {"from_user_id": 1, "is_like": true}

    Если is_like=true и адресат уже лайкнул тебя — создаётся Match,
    is_match=true и match_id в ответе.
    """
    from_user_id = body.from_user_id

    # Валидация: нельзя лайкать себя
    if from_user_id == to_user_id:
        raise HTTPException(status_code=400, detail="Cannot like yourself")

    # Проверяем что оба пользователя существуют
    from_user = await crud.get_user_by_id(db, from_user_id)
    if not from_user:
        raise HTTPException(status_code=404, detail=f"User {from_user_id} not found")

    to_user = await crud.get_user_by_id(db, to_user_id)
    if not to_user:
        raise HTTPException(status_code=404, detail=f"User {to_user_id} not found")

    # Сохраняем лайк
    like = await crud.create_or_update_like(db, from_user_id, to_user_id, body.is_like)

    # Проверяем взаимность
    is_match = False
    match_id = None
    match_score = None

    if body.is_like:
        mutual = await crud.check_mutual_like(db, from_user_id, to_user_id)
        if mutual:
            match_score = await _compute_match_score(db, from_user_id, to_user_id)
            match_db = await crud.create_match(db, from_user_id, to_user_id, match_score)
            is_match = True
            match_id = match_db.id

            # D4: создание AI-аватаров для обоих со-фаундеров при матче
            try:
                from_profile = await crud.get_founder_profile_by_user_id(db, from_user_id)
                if from_profile:
                    norm = from_profile.normalized_profile or {}
                    AvatarFactory.create_avatar(
                        user_id=from_user_id,
                        founder_name=norm.get("name", from_user.name or f"Founder {from_user_id}"),
                        role_id=str(norm.get("primary_role", "builder")),
                        match_id=match_db.id,
                        partner_user_id=to_user_id,
                    )
                to_profile = await crud.get_founder_profile_by_user_id(db, to_user_id)
                if to_profile:
                    norm = to_profile.normalized_profile or {}
                    AvatarFactory.create_avatar(
                        user_id=to_user_id,
                        founder_name=norm.get("name", to_user.name or f"Founder {to_user_id}"),
                        role_id=str(norm.get("primary_role", "builder")),
                        match_id=match_db.id,
                        partner_user_id=from_user_id,
                    )
            except Exception as e:
                logger.warning(f"Avatar creation failed: {e}")

            # D6: Telegram уведомления о матче (graceful — не ронять /like)
            try:
                from telegram_bot.notifications import send_match_notification
                asyncio.create_task(send_match_notification(
                    syndi_user_id=from_user_id,
                    partner_name=to_user.name or f"Founder {to_user_id}",
                    match_score=match_score or 0,
                ))
                asyncio.create_task(send_match_notification(
                    syndi_user_id=to_user_id,
                    partner_name=from_user.name or f"Founder {from_user_id}",
                    match_score=match_score or 0,
                ))
            except Exception as e:
                logger.warning(f"Telegram notification dispatch failed: {e}")

    return LikeResponse(
        like_id=like.id,
        from_user_id=like.from_user_id,
        to_user_id=like.to_user_id,
        is_like=like.is_like,
        is_match=is_match,
        match_id=match_id,
        match_score=match_score,
    )


@like_router.get("/matches", response_model=MatchesResponse)
async def get_matches(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Список взаимных матчей пользователя.

    Query: ?user_id=1

    Возвращает список MatchCard с partner_user_id, partner_name, match_score.
    """
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    matches_db = await crud.list_matches_for_user(db, user_id)

    cards = []
    for m in matches_db:
        partner_id = m.user_b_id if m.user_a_id == user_id else m.user_a_id
        partner = await crud.get_user_by_id(db, partner_id)
        cards.append(MatchCard(
            match_id=m.id,
            partner_user_id=partner_id,
            partner_name=partner.name if partner else str(partner_id),
            match_score=m.match_score,
            status=m.status,
        ))

    return MatchesResponse(
        user_id=user_id,
        matches=cards,
        total=len(cards),
    )

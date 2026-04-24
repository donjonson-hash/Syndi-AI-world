"""
discover_routes.py — Tinder-лента кандидатов.

GET /api/v1/discover?user_id={id}&limit={n}

Возвращает карточки кандидатов из founder_profiles, отсортированные
по FounderFit score, с фильтром уже лайкнутых/дизлайкнутых.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database import crud
from database.models import LikeDB, User as UserDB
from database.redis_client import cache_get, cache_set
from auth import get_current_user
from scoring import FounderProfile, score_pair, ScoreBreakdown
from sqlalchemy import select

discover_router = APIRouter(tags=["discover"])

DEFAULT_LIMIT = 10
MAX_LIMIT = 50


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class DiscoverCard(BaseModel):
    candidate_user_id: int
    candidate_name: str
    primary_role: str
    total_score: float
    intent_goal: str
    risk_flags: List[str]
    why: str


class DiscoverResponse(BaseModel):
    user_id: int
    cards: List[DiscoverCard]
    total: int
    filtered_already_seen: int   # сколько отфильтровано (уже лайкнутых/дизлайкнутых)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _fp_from_db(fp_record) -> Optional[FounderProfile]:
    """Восстанавливает FounderProfile из normalized_profile JSON."""
    try:
        return FounderProfile(**fp_record.normalized_profile)
    except Exception:
        return None


def _why_text(breakdown: ScoreBreakdown, candidate: FounderProfile) -> str:
    """Краткое объяснение совместимости."""
    parts = []
    if breakdown.intent_score >= 80:
        parts.append("одинаковые цели")
    if breakdown.role_score >= 80:
        parts.append("комплементарные роли")
    if breakdown.accountability_score >= 80:
        parts.append("высокая ответственность")
    if breakdown.tempo_score >= 80:
        parts.append("одинаковый темп")
    if breakdown.big5_openness_score is not None and breakdown.big5_openness_score >= 70:
        parts.append("психологическая совместимость")
    if not parts:
        parts.append("базовая совместимость")
    return ", ".join(parts[:3]).capitalize()


async def _get_seen_user_ids(db: AsyncSession, from_user_id: int) -> set:
    """Возвращает set user_id которых пользователь уже лайкал/дизлайкал."""
    result = await db.execute(
        select(LikeDB.to_user_id).where(LikeDB.from_user_id == from_user_id)
    )
    return {row[0] for row in result.fetchall()}


# ─── Endpoint ────────────────────────────────────────────────────────────────

@discover_router.get("/discover", response_model=DiscoverResponse)
async def get_discover(
    user_id: int = Query(..., description="ID текущего пользователя"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT, description="Кол-во карточек"),
    db: AsyncSession = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """
    Tinder-лента: карточки кандидатов, отсортированные по FounderFit score.

    - Берёт все активные founder_profiles кроме своего
    - Фильтрует уже лайкнутых/дизлайкнутых (те кому уже свайпнул)
    - Считает score_pair для каждого
    - Возвращает топ-{limit} по total_score

    Кэш: результат кэшируется в Redis на 60 секунд (ключ discover:{user_id}:{limit}).
    Если Redis недоступен — работает без кэша (graceful degradation).
    """
    cache_key = f"discover:{user_id}:{limit}"
    cached = await cache_get(cache_key)
    if cached is not None:
        try:
            return DiscoverResponse(**cached)
        except Exception:
            pass  # битый кэш — пересчитаем

    # Проверяем что пользователь существует
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Загружаем свой FounderProfile
    my_fp_record = await crud.get_founder_profile_by_user_id(db, user_id)
    if not my_fp_record:
        raise HTTPException(
            status_code=404,
            detail="Founder profile not found. Complete onboarding first."
        )
    my_profile = _fp_from_db(my_fp_record)
    if not my_profile:
        raise HTTPException(status_code=422, detail="Could not deserialize your founder profile")

    # Все кандидаты из founder_profiles (кроме себя)
    all_candidates = await crud.list_founder_profiles_exclude(db, exclude_user_id=user_id)

    # Кого уже видел (лайкал или дизлайкал)
    seen_ids = await _get_seen_user_ids(db, user_id)
    filtered_count = 0

    # Скорим и фильтруем
    scored: List[tuple] = []
    for fp_rec in all_candidates:
        candidate_profile = _fp_from_db(fp_rec)
        if not candidate_profile:
            continue

        # Фильтруем уже свайпнутых
        if fp_rec.user_id in seen_ids:
            filtered_count += 1
            continue

        try:
            breakdown = score_pair(my_profile, candidate_profile)
        except Exception:
            continue

        # Загружаем имя кандидата
        candidate_user = await crud.get_user_by_id(db, fp_rec.user_id)
        candidate_name = candidate_user.name if candidate_user else str(fp_rec.user_id)

        why = _why_text(breakdown, candidate_profile)

        card = DiscoverCard(
            candidate_user_id=fp_rec.user_id,
            candidate_name=candidate_name,
            primary_role=str(candidate_profile.primary_role),
            total_score=round(breakdown.total_compatibility_score, 1),
            intent_goal=str(candidate_profile.intent_goal),
            risk_flags=breakdown.risk_flags,
            why=why,
        )
        scored.append((breakdown.total_compatibility_score, card))

    # Сортируем по score desc, берём limit
    scored.sort(key=lambda x: x[0], reverse=True)
    top_cards = [card for _, card in scored[:limit]]

    response = DiscoverResponse(
        user_id=user_id,
        cards=top_cards,
        total=len(top_cards),
        filtered_already_seen=filtered_count,
    )

    # Кэшируем на 60 секунд (best-effort, молча игнорируем если Redis недоступен)
    try:
        await cache_set(cache_key, response.model_dump(), ttl=60)
    except Exception:
        pass

    return response

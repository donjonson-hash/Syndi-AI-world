"""
discover_routes.py — Tinder-лента кандидатов.

GET /api/v1/discover?user_id={id}&limit={n}

Возвращает карточки кандидатов из founder_profiles, отсортированные
по FounderFit score, с фильтром уже лайкнутых/дизлайкнутых.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
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
MIN_SCORE = 35.0       # Не показывать кандидатов с совместимостью ниже этого порога
HAS_BIG5_BONUS = 8.0   # Бонус к score когда оба профиля содержат Big Five данные


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class BigFiveMatch(BaseModel):
    """Big Five compatibility breakdown between two users."""
    openness: Optional[float] = None            # 0-100: совместимость по openness
    conscientiousness: Optional[float] = None    # 0-100: совместимость по conscientiousness
    extraversion: Optional[float] = None         # 0-100: совместимость по extraversion
    agreeableness: Optional[float] = None        # 0-100: совместимость по agreeableness
    emotional_stability: Optional[float] = None  # 0-100: совместимость по emotional_stability
    overall_fit: Optional[float] = None          # 0-100: weighted Big Five fit
    has_data: bool = False                       # True если оба профиля содержат Big Five


class DiscoverCard(BaseModel):
    candidate_user_id: int
    candidate_name: str
    primary_role: str
    total_score: float
    founder_fit_score: float
    intent_goal: str
    risk_flags: List[str]
    why: str
    big5: BigFiveMatch                            # Big Five compatibility breakdown
    tags: List[str] = Field(default_factory=list)  # human-readable теги совместимости


class DiscoverResponse(BaseModel):
    user_id: int
    cards: List[DiscoverCard]
    total: int
    filtered_already_seen: int
    min_score_threshold: float = MIN_SCORE


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _fp_from_db(fp_record) -> Optional[FounderProfile]:
    """Восстанавливает FounderProfile из normalized_profile JSON."""
    try:
        return FounderProfile(**fp_record.normalized_profile)
    except Exception:
        return None


def _build_big5_match(breakdown: ScoreBreakdown) -> BigFiveMatch:
    """Извлекает Big Five compatibility из ScoreBreakdown."""
    if breakdown.big5_fit_score is None:
        return BigFiveMatch(has_data=False)
    return BigFiveMatch(
        openness=breakdown.big5_openness_score,
        conscientiousness=breakdown.big5_conscientiousness_score,
        extraversion=breakdown.big5_extraversion_score,
        agreeableness=breakdown.big5_agreeableness_score,
        emotional_stability=breakdown.big5_emotional_stability_score,
        overall_fit=breakdown.big5_fit_score,
        has_data=True,
    )


def _build_tags(breakdown: ScoreBreakdown, me: FounderProfile, candidate: FounderProfile) -> List[str]:
    """Генерирует human-readable теги совместимости."""
    tags = []
    # Роли
    if breakdown.role_score >= 80:
        tags.append(f"🤝 Комплементарные роли: {me.primary_role} + {candidate.primary_role}")
    elif me.primary_role == candidate.primary_role:
        tags.append(f"⚠️ Одинаковые роли: оба {me.primary_role}")
    # Цели
    if breakdown.intent_score >= 80:
        tags.append("🎯 Одинаковые цели")
    elif breakdown.intent_score >= 60:
        tags.append("🎯 Похожие цели")
    # Темп
    if breakdown.tempo_score >= 70:
        tags.append("⚡ Совпадает темп работы")
    # Accountability
    if breakdown.accountability_score >= 80:
        tags.append("🔒 Высокая взаимная ответственность")
    elif breakdown.accountability_score < 40:
        tags.append("⚠️ Разный уровень ответственности")
    # Big Five highlights
    if breakdown.big5_fit_score is not None:
        if breakdown.big5_fit_score >= 75:
            tags.append("🧠 Сильная психологическая совместимость")
        elif breakdown.big5_fit_score >= 60:
            tags.append("🧠 Хорошая психологическая совместимость")
        # Specific Big Five insights
        if breakdown.big5_conscientiousness_score and breakdown.big5_conscientiousness_score >= 80:
            tags.append("📋 Оба дисциплинированны в исполнении")
        if breakdown.big5_openness_score and breakdown.big5_openness_score >= 80:
            tags.append("🎨 Оба открыты новому")
        if breakdown.big5_extraversion_score and breakdown.big5_extraversion_score >= 80:
            tags.append("💬 Оба коммуникабельны")
    return tags[:5]  # максимум 5 тегов


def _why_text(breakdown: ScoreBreakdown, me: FounderProfile, candidate: FounderProfile) -> str:
    """Подробное объяснение совместимости — с Big Five инсайтами."""
    parts = []
    # FounderFit highlights
    if breakdown.role_score >= 80:
        parts.append(f"комплементарные роли ({me.primary_role} + {candidate.primary_role})")
    if breakdown.intent_score >= 80:
        parts.append("совпадают цели")
    if breakdown.accountability_score >= 80:
        parts.append("высокая ответственность")
    if breakdown.tempo_score >= 70:
        parts.append(f"похожий темп ({me.tempo} ↔ {candidate.tempo})")
    # Big Five insights
    if breakdown.big5_fit_score is not None:
        if breakdown.big5_fit_score >= 75:
            parts.append("сильная психологическая совместимость")
        if breakdown.big5_conscientiousness_score and breakdown.big5_conscientiousness_score >= 80:
            parts.append("оба дисциплинированны")
        if breakdown.big5_openness_score and breakdown.big5_openness_score >= 75:
            parts.append("оба открыты новому")
        if breakdown.big5_extraversion_score and breakdown.big5_extraversion_score >= 75:
            parts.append("общительная пара")
    if not parts:
        parts.append("базовая совместимость")
    return ", ".join(parts[:4]).capitalize()


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

        # Фильтр по минимальному порогу совместимости
        if breakdown.total_compatibility_score < MIN_SCORE:
            continue

        why = _why_text(breakdown, my_profile, candidate_profile)
        big5_match = _build_big5_match(breakdown)
        tags = _build_tags(breakdown, my_profile, candidate_profile)

        card = DiscoverCard(
            candidate_user_id=fp_rec.user_id,
            candidate_name=candidate_name,
            primary_role=str(candidate_profile.primary_role),
            total_score=round(breakdown.total_compatibility_score, 1),
            founder_fit_score=round(breakdown.founder_fit_score, 1),
            intent_goal=str(candidate_profile.intent_goal),
            risk_flags=breakdown.risk_flags,
            why=why,
            big5=big5_match,
            tags=tags,
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

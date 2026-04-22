"""
Syndi Match API — FastAPI backend
Founder matching engine v0.1
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uvicorn

from database.database import get_db
from database.crud import get_user_by_name, get_all_candidates, get_user_by_id
from services.matching import MatchingService
from scoring import FounderProfile, score_pair, SCORING_MODEL_VERSION
from questionnaire_normalizer import normalize, ONBOARDING_SCHEMA_VERSION

app = FastAPI(
    title="Syndi Match API",
    description="Founder matching engine — FounderFit v0.1 + Big Five modifier",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

matching_service = MatchingService()


# ── System ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status": "Syndi Match API is running",
        "scoring_model": SCORING_MODEL_VERSION,
        "onboarding_schema": ONBOARDING_SCHEMA_VERSION,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ── Onboarding ────────────────────────────────────────────────────────────────

class OnboardingSubmit(BaseModel):
    user_id: str
    time_commitment_hours_per_week: float
    no_salary_readiness_months: float
    intent_goal: str
    launched_projects_count: float
    self_execution_breadth: float
    primary_role: str
    no_go_roles: List[str] = []
    decision_style: str
    conflict_style: str
    work_mode: str
    tempo: str
    sync_frequency_per_week: float
    accountability_disappear_risk: int
    accountability_ownership_drive: int
    big5: Optional[Dict[str, List[int]]] = None


@app.post("/api/v1/onboarding/submit")
async def submit_onboarding(payload: OnboardingSubmit):
    """
    Принимает raw ответы, нормализует в FounderProfile.
    В продакшне здесь нужно сохранять профиль в БД.
    """
    try:
        profile = normalize(payload.model_dump())
        return {
            "status": "ok",
            "user_id": profile.user_id,
            "normalized_profile": profile.model_dump(),
            "schema_version": ONBOARDING_SCHEMA_VERSION,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Matching ──────────────────────────────────────────────────────────────────

class PairScoreRequest(BaseModel):
    profile_a: Dict[str, Any]
    profile_b: Dict[str, Any]


@app.post("/api/v1/matches/score-pair")
async def score_two_profiles(payload: PairScoreRequest):
    """
    Считает совместимость двух нормализованных FounderProfile напрямую.
    Удобно для отладки и внутреннего тестирования.
    """
    try:
        a = FounderProfile(**payload.profile_a)
        b = FounderProfile(**payload.profile_b)
        result = score_pair(a, b)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


class GenerateMatchesRequest(BaseModel):
    requester: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    limit: int = 3
    exclude_risk_flags: List[str] = []


@app.post("/api/v1/matches/generate")
async def generate_matches(payload: GenerateMatchesRequest):
    """
    Принимает raw ответы requester и список кандидатов,
    возвращает shortlist топ-N по total_compatibility_score.
    """
    try:
        results = matching_service.match_founder(
            payload.requester, payload.candidates
        )
        if payload.exclude_risk_flags:
            results = matching_service.filter_by_risk(results, payload.exclude_risk_flags)
        shortlist = matching_service.get_shortlist(results, limit=payload.limit)
        return {
            "total_candidates": len(payload.candidates),
            "shortlist_size": len(shortlist),
            "scoring_model": SCORING_MODEL_VERSION,
            "matches": [r.to_dict() for r in shortlist],
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Legacy DB endpoints (из старого main.py) ──────────────────────────────────

class MatchResponse(BaseModel):
    founder_name: str
    candidate_name: str
    match_score: float
    ai_interpretation: str
    skills_score: float
    enneagram_score: float


@app.get("/api/v1/match/{founder_name}")
async def match_founder_legacy(
    founder_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Legacy endpoint — матчинг из SQLite БД по имени фаундера."""
    founder = await get_user_by_name(db, founder_name)
    if not founder:
        raise HTTPException(status_code=404, detail=f"Founder '{founder_name}' not found")

    candidates = await get_all_candidates(db, exclude_user_id=founder.id)
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")

    # Используем новый MatchingService если есть normalized_profile в psycho_profile
    results = []
    for c in candidates:
        f_data = founder.to_dict()
        c_data = c.to_dict()
        # Проверяем есть ли founder-специфичные поля
        f_np = f_data.get("psycho_profile", {})
        c_np = c_data.get("psycho_profile", {})
        if f_np.get("intent_goal") and c_np.get("intent_goal"):
            try:
                a = FounderProfile(**f_np)
                b = FounderProfile(**c_np)
                bd = score_pair(a, b)
                results.append({
                    "founder_name": founder.name,
                    "candidate_name": c.name,
                    "match_score": bd.total_compatibility_score,
                    "ai_interpretation": _interpret(bd),
                    "skills_score": bd.role_score,
                    "enneagram_score": bd.work_style_score,
                })
                continue
            except Exception:
                pass
        # Fallback: старая логика через enneagram/skills JSON
        from core.ai.matching_engine import MatchingEngine
        engine = MatchingEngine()
        score, text = engine.calculate_match(f_data, c_data)
        results.append({
            "founder_name": founder.name,
            "candidate_name": c.name,
            "match_score": round(score, 2),
            "ai_interpretation": text,
            "skills_score": 0.0,
            "enneagram_score": 0.0,
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:3]


def _interpret(bd) -> str:
    s = bd.total_compatibility_score
    flags = bd.risk_flags
    if s >= 80:
        return (f"Высокая совместимость ({s:.0f}%). "
                f"FounderFit: {bd.founder_fit_score:.0f}%. "
                + (f"Risk flags: {', '.join(flags)}" if flags else "Нет флагов риска."))
    elif s >= 55:
        return (f"Средняя совместимость ({s:.0f}%). "
                + (f"Обратите внимание: {', '.join(flags)}." if flags else "Потенциал для роста."))
    else:
        return (f"Низкая совместимость ({s:.0f}%). "
                f"Флаги: {', '.join(flags) if flags else 'нет'}.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

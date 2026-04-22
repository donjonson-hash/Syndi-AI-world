"""
Syndi AI — Unified API
Tinder for Co-Founders: matching engine + AI agents + Big Five

Объединяет все endpoints в одно приложение:
  - Onboarding (raw questionnaire → normalized profile)
  - Matching (FounderFit + Big5 scoring)
  - Users CRUD
  - Big Five test
  - AI Agents (Kristina)
  - Legacy DB matching
"""

import os
import sys
import logging
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

# ── Ensure backend/ is on sys.path ───────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from database.database import get_db, init_db, close_db
from database import crud
from models.big_five import BigFiveTest, TestSubmission
from models.user import UserCreate
from scoring import FounderProfile, score_pair, SCORING_MODEL_VERSION
from questionnaire_normalizer import normalize, ONBOARDING_SCHEMA_VERSION
from services.matching import MatchingService
from agents.kristina_routes import router as kristina_router

logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════════════════════
# App
# ═════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Syndi AI — Co-Founder Matching Platform",
    description="Находим идеальных сооснователей по психологической совместимости и комплементарности навыков.",
    version="1.3.0",
)

# ── CORS — для разработки разрешаем всё, в проде настраивается через env ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для локальной разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting (простая in-memory реализация для MVP) ──────────────────
from collections import defaultdict
import time

_rate_store: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _rate_store[client_ip]
    # очищаем записи старше 60 секунд
    _rate_store[client_ip] = [t for t in window if now - t < 60]
    if len(_rate_store[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    _rate_store[client_ip].append(now)
    response = await call_next(request)
    return response


# ── Request ID ────────────────────────────────────────────────────────────
import uuid as _uuid

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(_uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Services ──────────────────────────────────────────────────────────────
matching_service = MatchingService()
big_five_test = BigFiveTest()

# In-memory хранилище профилей (MVP; заменить на БД в след. спринте)
_profiles: Dict[str, FounderProfile] = {}


# ═════════════════════════════════════════════════════════════════════════════
# Lifecycle
# ═════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info(f"Database ready | Scoring: {SCORING_MODEL_VERSION} | Schema: {ONBOARDING_SCHEMA_VERSION}")


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# ═════════════════════════════════════════════════════════════════════════════
# System (информация о версии перенесена на /api/info)
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/info")
async def api_info():
    return {
        "name": "Syndi AI — Co-Founder Matching Platform",
        "version": "1.3.0",
        "scoring_model": SCORING_MODEL_VERSION,
        "onboarding_schema": ONBOARDING_SCHEMA_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.3.0", "database": "connected"}


# ═════════════════════════════════════════════════════════════════════════════
# Onboarding — принимает raw ответы и нормализованные данные
# ═════════════════════════════════════════════════════════════════════════════

class RawQuestionnaire(BaseModel):
    """Raw ответы фронтенда — поля анкеты в человекочитаемом виде."""
    user_id: str
    time_commitment: str
    no_salary_readiness: str
    intent_goal: str
    launched_projects: str
    self_actions: List[str]
    primary_role: str
    no_go_role_tags: List[str] = []
    decision_style: str
    conflict_style: str
    work_mode: str
    tempo: str
    sync_frequency: str
    accountability_disappear_label: str
    accountability_ownership_label: str
    big5_o_1:  Optional[int] = None
    big5_o_2:  Optional[int] = None
    big5_c_1:  Optional[int] = None
    big5_c_2:  Optional[int] = None
    big5_c_3:  Optional[int] = None
    big5_e_1:  Optional[int] = None
    big5_e_2:  Optional[int] = None
    big5_a_1:  Optional[int] = None
    big5_a_2:  Optional[int] = None
    big5_es_1: Optional[int] = None
    big5_es_2: Optional[int] = None


class OnboardingSubmit(BaseModel):
    """Normalized ответы (прямой формат для scoring engine)."""
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


def _map_raw_to_normalizer(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Переводит RawQuestionnaire → формат normalize()."""
    TIME_MAP = {"full_time": 40, "part_time": 20, "10h": 10, "40h": 40, "60h": 60, "80h": 80}
    SALARY_MAP = {"3_months": 3, "6_months": 6, "12_months": 12, "18_months": 18, "24_months": 24}
    LAUNCHED_MAP = {"0": 0, "1": 1, "1-2": 1, "2": 2, "3+": 7, "5+": 9}
    SYNC_MAP = {"daily": 7, "every_other_day": 4, "twice_a_week": 2, "weekly": 1, "as_needed": 1}
    DISAPPEAR_MAP = {"never": 5, "rarely": 4, "sometimes": 3, "often": 2, "always": 1}
    OWNERSHIP_MAP = {"always": 5, "usually": 4, "sometimes": 3, "rarely": 2, "never": 1}

    def b5_group(keys):
        vals = [raw.get(k) for k in keys if raw.get(k) is not None]
        while len(vals) < 4:
            vals.append(vals[-1] if vals else 3)
        return vals[:4]

    big5 = None
    b5_keys = ["big5_o_1", "big5_o_2", "big5_c_1", "big5_c_2", "big5_c_3",
               "big5_e_1", "big5_e_2", "big5_a_1", "big5_a_2", "big5_es_1", "big5_es_2"]
    if any(raw.get(k) is not None for k in b5_keys):
        big5 = {
            "openness":            b5_group(["big5_o_1", "big5_o_2", "big5_o_1", "big5_o_2"]),
            "conscientiousness":   b5_group(["big5_c_1", "big5_c_2", "big5_c_3", "big5_c_1"]),
            "extraversion":        b5_group(["big5_e_1", "big5_e_2", "big5_e_1", "big5_e_2"]),
            "agreeableness":       b5_group(["big5_a_1", "big5_a_2", "big5_a_1", "big5_a_2"]),
            "emotional_stability": b5_group(["big5_es_1", "big5_es_1", "big5_es_2", "big5_es_2"]),
        }

    tc_str = str(raw.get("time_commitment", "40h")).lower()
    tc_val = TIME_MAP.get(tc_str, 40)
    try:
        tc_val = float(tc_str.replace("h", "")) if "h" in tc_str else tc_val
    except ValueError:
        pass

    return {
        "user_id": raw["user_id"],
        "time_commitment_hours_per_week": tc_val,
        "no_salary_readiness_months": SALARY_MAP.get(str(raw.get("no_salary_readiness", "6_months")).lower(), 6),
        "intent_goal": raw["intent_goal"],
        "launched_projects_count": LAUNCHED_MAP.get(str(raw.get("launched_projects", "0")).lower(), 0),
        "self_execution_breadth": min(len(raw.get("self_actions", [])) * 2.5, 10),
        "primary_role": raw["primary_role"],
        "no_go_roles": raw.get("no_go_role_tags", []),
        "decision_style": raw["decision_style"],
        "conflict_style": raw["conflict_style"],
        "work_mode": raw["work_mode"],
        "tempo": raw["tempo"],
        "sync_frequency_per_week": SYNC_MAP.get(str(raw.get("sync_frequency", "twice_a_week")).lower(), 2),
        "accountability_disappear_risk": DISAPPEAR_MAP.get(str(raw.get("accountability_disappear_label", "sometimes")).lower(), 3),
        "accountability_ownership_drive": OWNERSHIP_MAP.get(str(raw.get("accountability_ownership_label", "usually")).lower(), 4),
        "big5": big5,
    }


@app.post("/api/v1/onboarding/raw")
async def submit_raw_questionnaire(data: RawQuestionnaire):
    """Принимает raw ответы анкеты фронтенда, нормализует, сохраняет профиль."""
    raw = {k: v for k, v in data.model_dump().items() if v is not None}
    try:
        mapped = _map_raw_to_normalizer(raw)
        profile = normalize(mapped)
        _profiles[profile.user_id] = profile
        return {
            "status": "success",
            "user_id": profile.user_id,
            "intent": profile.intent_goal,
            "normalized_profile": profile.model_dump(),
            "schema_version": ONBOARDING_SCHEMA_VERSION,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/v1/onboarding/submit")
async def submit_onboarding(payload: OnboardingSubmit):
    """Принимает уже нормализованные данные, сохраняет профиль."""
    try:
        profile = normalize(payload.model_dump())
        _profiles[profile.user_id] = profile
        return {
            "status": "ok",
            "user_id": profile.user_id,
            "normalized_profile": profile.model_dump(),
            "schema_version": ONBOARDING_SCHEMA_VERSION,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# Matching
# ═════════════════════════════════════════════════════════════════════════════

class MatchCard(BaseModel):
    candidate_id: str
    total_score: float
    why_there_is_a_chance: str
    risks: List[str]


class PairScoreRequest(BaseModel):
    profile_a: Dict[str, Any]
    profile_b: Dict[str, Any]


class GenerateMatchesRequest(BaseModel):
    requester: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    limit: int = 3
    exclude_risk_flags: List[str] = []


@app.get("/api/v1/match/{user_id}", response_model=List[MatchCard])
async def find_matches(user_id: str):
    """Топ-3 кандидата по FounderFit + Big5 скорингу."""
    founder = _profiles.get(user_id)
    if not founder:
        raise HTTPException(status_code=404, detail="Profile not found. Submit /api/v1/onboarding first.")
    candidates = [p for uid, p in _profiles.items() if uid != user_id]
    if not candidates:
        raise HTTPException(status_code=404, detail="No other candidates yet")
    results = []
    for c in candidates:
        score = score_pair(founder, c)
        reasons = []
        if score.role_score >= 80:
            reasons.append("разные сильные стороны (комплементарные роли)")
        if score.intent_score >= 70:
            reasons.append("одинаковый уровень вовлечённости")
        if score.tempo_score >= 70:
            reasons.append("совпадает темп работы")
        results.append(MatchCard(
            candidate_id=c.user_id,
            total_score=score.total_compatibility_score,
            why_there_is_a_chance="; ".join(reasons) if reasons else "Basic compatibility",
            risks=score.risk_flags,
        ))
    results.sort(key=lambda x: x.total_score, reverse=True)
    return results[:3]


@app.post("/api/v1/matches/score-pair")
async def score_two_profiles(payload: PairScoreRequest):
    """Считает совместимость двух нормализованных FounderProfile."""
    try:
        a = FounderProfile(**payload.profile_a)
        b = FounderProfile(**payload.profile_b)
        return score_pair(a, b).model_dump()
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/v1/matches/generate")
async def generate_matches(payload: GenerateMatchesRequest):
    """Принимает requester + кандидатов, возвращает shortlist."""
    try:
        results = matching_service.match_founder(payload.requester, payload.candidates)
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


# ═════════════════════════════════════════════════════════════════════════════
# Users CRUD
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_dict = user_data.dict()
    user_dict["id"] = str(uuid4())
    user = await crud.create_user(db, user_dict)
    return {"id": user.id, "email": user.email, "name": user.name}


@app.get("/api/v1/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db)
    return [{"id": u.id, "email": u.email, "name": u.name} for u in users]


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name}


# ═════════════════════════════════════════════════════════════════════════════
# Big Five Test
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/test/questions")
async def get_questions():
    questions = big_five_test.get_questions()
    return {"questions": [{"id": q["id"], "text": q["text"], "trait": q["trait"]} for q in questions]}


@app.post("/api/v1/test/submit")
async def submit_test(submission: TestSubmission, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, str(submission.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = big_five_test.calculate_profile(submission.answers)
    scores = {
        "openness": profile.openness,
        "conscientiousness": profile.conscientiousness,
        "extraversion": profile.extraversion,
        "agreeableness": profile.agreeableness,
        "neuroticism": profile.neuroticism,
    }
    await crud.create_big_five_result(db, str(submission.user_id), scores)
    return {"user_id": str(submission.user_id), "profile": scores}


# ═════════════════════════════════════════════════════════════════════════════
# AI Agents — Kristina
# ═════════════════════════════════════════════════════════════════════════════

app.include_router(kristina_router)


@app.get("/api/v1/agents")
async def list_agents():
    from agents.kristina import KristinaUXDesigner
    kristina = KristinaUXDesigner()
    return {"agents": [kristina.get_info()]}


# ═════════════════════════════════════════════════════════════════════════════
# Legacy DB endpoint
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/legacy/match/{founder_name}")
async def match_founder_legacy(founder_name: str, db: AsyncSession = Depends(get_db)):
    """Legacy — матчинг из SQLite по имени фаундера."""
    from database.crud import get_user_by_name, get_all_candidates
    founder = await get_user_by_name(db, founder_name)
    if not founder:
        raise HTTPException(status_code=404, detail=f"Founder '{founder_name}' not found")
    candidates = await get_all_candidates(db, exclude_user_id=founder.id)
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")

    results = []
    for c in candidates:
        f_np = founder.to_dict().get("psycho_profile", {})
        c_np = c.to_dict().get("psycho_profile", {})
        if f_np.get("intent_goal") and c_np.get("intent_goal"):
            try:
                bd = score_pair(FounderProfile(**f_np), FounderProfile(**c_np))
                results.append({
                    "candidate": c.name,
                    "score": bd.total_compatibility_score,
                    "risks": bd.risk_flags,
                })
                continue
            except Exception:
                pass
        results.append({"candidate": c.name, "score": 0.0, "risks": ["legacy_fallback"]})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]


# ═════════════════════════════════════════════════════════════════════════════
# Legacy aliases (обратная совместимость со старыми путями и упрощённые URL для фронтенда)
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/onboarding")
async def legacy_onboarding(data: RawQuestionnaire):
    """Alias: /onboarding -> /api/v1/onboarding/raw"""
    return await submit_raw_questionnaire(data)


@app.get("/match/{user_id}", response_model=List[MatchCard])
async def legacy_match(user_id: str):
    """Alias: /match/{user_id} -> /api/v1/match/{user_id}"""
    return await find_matches(user_id)


@app.get("/bigfive/questions")
async def legacy_bigfive_questions():
    """Alias: /bigfive/questions -> /api/v1/test/questions"""
    return await get_questions()


@app.post("/bigfive/submit")
async def legacy_bigfive_submit(submission: TestSubmission, db: AsyncSession = Depends(get_db)):
    """Alias: /bigfive/submit -> /api/v1/test/submit"""
    return await submit_test(submission, db)


@app.post("/users")
async def legacy_create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Alias: /users -> /api/v1/users"""
    return await create_user(user_data, db)


@app.get("/users")
async def legacy_list_users(db: AsyncSession = Depends(get_db)):
    """Alias"""
    return await list_users(db)


@app.get("/users/{user_id}")
async def legacy_get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Alias"""
    return await get_user(user_id, db)


@app.get("/agents")
async def legacy_list_agents():
    """Alias"""
    return await list_agents()


# ═════════════════════════════════════════════════════════════════════════════
# Static files (должен быть после всех маршрутов)
# ═════════════════════════════════════════════════════════════════════════════

# Папка static должна существовать с файлами index.html, style.css, app.js
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Syndi AI — starting unified API...")
    print("Web interface: http://127.0.0.1:8000")
    print("API docs: http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

"""
Syndi Tinder-Founder API
Версия: 1.2.0

Объединяет:
  - оригинальный api/main.py (users, Big Five test, DB, agents)
  - новые эндпоинты из main.py (RawQuestionnaire, /onboarding, /match)

Scoring-движок: services/scoring.py + services/questionnaire_normalizer.py
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from uuid import uuid4
import sys
import uvicorn
from pathlib import Path

# services/ лежат в backend/, добавляем его в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db, init_db, close_db
from db import crud

from models.big_five import BigFiveTest, TestSubmission
from models.user import UserCreate

# ── Scoring-движок SyndiAI v0.1 ───────────────────────────────────────────────
from services.scoring import FounderProfile, score_pair, SCORING_MODEL_VERSION
from services.questionnaire_normalizer import normalize, ONBOARDING_SCHEMA_VERSION

# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Syndi Tinder-Founder API",
    description="Отсекаем туристов. Находим сооснователей.",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

big_five_test = BigFiveTest()

# In-memory хранилище нормализованных профилей
# (заменить на БД через founder_profiles таблицу в следующем спринте)
_profiles: Dict[str, FounderProfile] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    await init_db()
    print("✓ Database ready")
    print(f"✓ Scoring model: {SCORING_MODEL_VERSION}")


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# ─────────────────────────────────────────────────────────────────────────────
# System
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Syndi Tinder-Founder API",
        "version": "1.2.0",
        "scoring_model": SCORING_MODEL_VERSION,
        "onboarding_schema": ONBOARDING_SCHEMA_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class RawQuestionnaire(BaseModel):
    """Raw ответы фронтенда — поля анкеты в человекочитаемом виде."""
    user_id: str

    # Intent
    time_commitment: str           # "full_time" | "part_time" | ...
    no_salary_readiness: str       # "6_months" | "12_months" | ...
    intent_goal: str               # "build_company" | "try_idea" | ...

    # Experience
    launched_projects: str         # "0" | "1-2" | "3+"
    self_actions: List[str]        # ["built_mvp", "sold", ...]

    # Role
    primary_role: str              # "builder" | "seller" | ...
    no_go_role_tags: List[str]     # ["builder", ...]

    # Work style
    decision_style: str
    conflict_style: str
    work_mode: str

    # Tempo
    tempo: str
    sync_frequency: str

    # Accountability
    accountability_disappear_label: str
    accountability_ownership_label: str

    # Big Five (опционально, Likert 1–5)
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


class MatchCard(BaseModel):
    """Карточка матча — формат выдачи."""
    candidate_id: str
    total_score: float
    why_there_is_a_chance: str
    risks: List[str]


# ─────────────────────────────────────────────────────────────────────────────
# Tinder-Founder endpoints
# ─────────────────────────────────────────────────────────────────────────────

def _map_raw_to_normalizer(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Переводит поля RawQuestionnaire в формат questionnaire_normalizer.normalize().

    RawQuestionnaire использует строковые метки (time_commitment="full_time"),
    normalizer ожидает числовые значения (time_commitment_hours_per_week=40).
    """
    TIME_MAP = {
        "full_time": 40, "part_time": 20, "10h": 10,
        "40h": 40, "60h": 60, "80h": 80,
    }
    SALARY_MAP = {
        "3_months": 3, "6_months": 6, "12_months": 12,
        "18_months": 18, "24_months": 24,
    }
    LAUNCHED_MAP = {"0": 0, "1": 1, "1-2": 1, "2": 2, "3+": 7, "5+": 9}
    BREADTH_MAP  = {"low": 2, "medium": 5, "high": 8}
    SYNC_MAP     = {
        "daily": 7, "every_other_day": 4, "twice_a_week": 2,
        "weekly": 1, "as_needed": 1,
    }
    DISAPPEAR_MAP = {"never": 5, "rarely": 4, "sometimes": 3, "often": 2, "always": 1}
    OWNERSHIP_MAP = {"always": 5, "usually": 4, "sometimes": 3, "rarely": 2, "never": 1}

    # Big Five — собираем Likert-ответы в группы по 4 вопроса (минимум 2 есть)
    def b5_group(keys):
        vals = [raw.get(k) for k in keys if raw.get(k) is not None]
        # Дублируем если только 2 вопроса — normalizer ожидает 4
        while len(vals) < 4:
            vals.append(vals[-1] if vals else 3)
        return vals[:4]

    big5 = None
    b5_keys = ["big5_o_1", "big5_o_2", "big5_c_1", "big5_c_2",
               "big5_c_3", "big5_e_1", "big5_e_2", "big5_a_1",
               "big5_a_2", "big5_es_1", "big5_es_2"]
    if any(raw.get(k) is not None for k in b5_keys):
        big5 = {
            "openness":            b5_group(["big5_o_1",  "big5_o_2",  "big5_o_1",  "big5_o_2"]),
            "conscientiousness":   b5_group(["big5_c_1",  "big5_c_2",  "big5_c_3",  "big5_c_1"]),
            "extraversion":        b5_group(["big5_e_1",  "big5_e_2",  "big5_e_1",  "big5_e_2"]),
            "agreeableness":       b5_group(["big5_a_1",  "big5_a_2",  "big5_a_1",  "big5_a_2"]),
            "emotional_stability": b5_group(["big5_es_1", "big5_es_1", "big5_es_2", "big5_es_2"]),  # es1=reversed pair, es2=direct pair
        }

    tc_str = str(raw.get("time_commitment", "40h")).lower()
    tc_val = TIME_MAP.get(tc_str, 40)
    try:
        tc_val = float(tc_str.replace("h", "")) if "h" in tc_str else tc_val
    except ValueError:
        pass

    sal_str = str(raw.get("no_salary_readiness", "6_months")).lower()
    sal_val = SALARY_MAP.get(sal_str, 6)

    lp_str  = str(raw.get("launched_projects", "0")).lower()
    lp_val  = LAUNCHED_MAP.get(lp_str, 0)

    breadth_list = raw.get("self_actions", [])
    breadth_val  = min(len(breadth_list) * 2.5, 10)

    sync_str = str(raw.get("sync_frequency", "twice_a_week")).lower()
    sync_val = SYNC_MAP.get(sync_str, 2)

    dis_str  = str(raw.get("accountability_disappear_label", "sometimes")).lower()
    dis_val  = DISAPPEAR_MAP.get(dis_str, 3)
    own_str  = str(raw.get("accountability_ownership_label", "usually")).lower()
    own_val  = OWNERSHIP_MAP.get(own_str, 4)

    return {
        "user_id": raw["user_id"],
        "time_commitment_hours_per_week": tc_val,
        "no_salary_readiness_months":     sal_val,
        "intent_goal":                    raw["intent_goal"],
        "launched_projects_count":        lp_val,
        "self_execution_breadth":         breadth_val,
        "primary_role":                   raw["primary_role"],
        "no_go_roles":                    raw.get("no_go_role_tags", []),
        "decision_style":                 raw["decision_style"],
        "conflict_style":                 raw["conflict_style"],
        "work_mode":                      raw["work_mode"],
        "tempo":                          raw["tempo"],
        "sync_frequency_per_week":        sync_val,
        "accountability_disappear_risk":  dis_val,
        "accountability_ownership_drive": own_val,
        "big5":                           big5,
    }


@app.post("/onboarding")
async def submit_questionnaire(data: RawQuestionnaire):
    """Принимает raw ответы анкеты, нормализует, кладёт в in-memory профиль."""
    raw = {k: v for k, v in data.model_dump().items() if v is not None}
    try:
        mapped  = _map_raw_to_normalizer(raw)
        profile = normalize(mapped)
        _profiles[profile.user_id] = profile
        return {
            "status":  "success",
            "message": "Профиль сформирован",
            "user_id": profile.user_id,
            "intent":  profile.intent_goal,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/match/{user_id}", response_model=List[MatchCard])
async def find_matches(user_id: str):
    """Ищем топ-3 кандидата по FounderFit + Big5 скорингу."""
    founder = _profiles.get(user_id)
    if not founder:
        raise HTTPException(status_code=404, detail="Пройди опрос сначала (/onboarding)")

    candidates = [p for uid, p in _profiles.items() if uid != user_id]
    if not candidates:
        raise HTTPException(status_code=404, detail="В базе пока нет других кандидатов")

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
            why_there_is_a_chance="; ".join(reasons) if reasons else "Базовое совпадение",
            risks=score.risk_flags,
        ))

    results.sort(key=lambda x: x.total_score, reverse=True)
    return results[:3]


# ─────────────────────────────────────────────────────────────────────────────
# Оригинальные endpoints (users / Big Five / agents)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/test/questions")
async def get_questions():
    """Big Five — список вопросов."""
    questions = big_five_test.get_questions()
    return [{"id": q["id"], "text": q["text"], "trait": q["trait"]} for q in questions]


@app.post("/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создать пользователя."""
    existing = await crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_dict = user_data.dict()
    user_dict["id"] = str(uuid4())
    user = await crud.create_user(db, user_dict)
    return {"id": user.id, "email": user.email, "name": user.name, "message": "User created"}


@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db)
    return [{"id": u.id, "email": u.email, "name": u.name} for u in users]


@app.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name}


@app.post("/test/submit")
async def submit_test(submission: TestSubmission, db: AsyncSession = Depends(get_db)):
    """Отправить результаты Big Five теста."""
    user = await crud.get_user(db, str(submission.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = big_five_test.calculate_profile(submission.answers)
    scores = {
        "openness":          profile.openness,
        "conscientiousness": profile.conscientiousness,
        "extraversion":      profile.extraversion,
        "agreeableness":     profile.agreeableness,
        "neuroticism":       profile.neuroticism,
    }
    await crud.create_big_five_result(db, str(submission.user_id), scores)
    return {"user_id": str(submission.user_id), "profile": scores, "message": "Results saved"}


@app.get("/agents")
async def list_agents():
    return {"agents": [{"id": "kristina", "name": "Kristina", "role": "UX Designer"}]}


if __name__ == "__main__":
    print("🚀 Запуск Syndi Tinder-Founder API...")
    print("🔗 Документация: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

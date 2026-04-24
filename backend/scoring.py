"""
SyndiAI Founder Matching — Core Pair Scoring Engine
Model version: syndiai-founder-v0.1

Формула:
  FounderFit = 0.25·Intent + 0.20·Role + 0.20·Tempo + 0.15·WorkStyle + 0.15·Accountability + 0.05·Experience
  Compatibility = 0.80·FounderFit + 0.20·Big5Fit   (если Big Five есть)
  Compatibility = FounderFit                         (если Big Five нет)
"""
from __future__ import annotations
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

SCORING_MODEL_VERSION = "syndiai-founder-v0.1"

IntentGoal    = Literal["try_idea", "stable_income", "build_company", "gain_experience"]
RoleType      = Literal["builder", "seller", "operator", "researcher"]
DecisionStyle = Literal["fast_risky", "analyze_first", "discuss_first", "delay_until_clear"]
ConflictStyle = Literal["avoid", "calm_discussion", "direct_clash", "depends"]
WorkMode      = Literal["solo", "tight_pair", "team", "any"]
TempoType     = Literal["iterate_fast", "build_right_first"]


class BigFiveProfile(BaseModel):
    openness: float = Field(ge=0, le=100)
    conscientiousness: float = Field(ge=0, le=100)
    extraversion: float = Field(ge=0, le=100)
    agreeableness: float = Field(ge=0, le=100)
    emotional_stability: float = Field(ge=0, le=100)


class FounderProfile(BaseModel):
    user_id: str
    time_commitment: float = Field(ge=0, le=100)
    no_salary_readiness: float = Field(ge=0, le=100)
    intent_goal: IntentGoal
    launched_projects: float = Field(ge=0, le=100)
    self_execution_breadth: float = Field(ge=0, le=100)
    primary_role: RoleType
    no_go_roles: List[RoleType] = Field(default_factory=list)
    decision_style: DecisionStyle
    conflict_style: ConflictStyle
    work_mode: WorkMode
    tempo: TempoType
    sync_frequency: float = Field(ge=0, le=100)
    accountability_disappear: float = Field(ge=0, le=100)
    accountability_ownership: float = Field(ge=0, le=100)
    big5: Optional[BigFiveProfile] = None


class ScoreBreakdown(BaseModel):
    model_config = {"protected_namespaces": ()}

    intent_score: float
    role_score: float
    tempo_score: float
    work_style_score: float
    accountability_score: float
    experience_score: float
    founder_fit_score: float
    big5_openness_score: Optional[float] = None
    big5_conscientiousness_score: Optional[float] = None
    big5_extraversion_score: Optional[float] = None
    big5_agreeableness_score: Optional[float] = None
    big5_emotional_stability_score: Optional[float] = None
    big5_fit_score: Optional[float] = None
    total_compatibility_score: float
    risk_flags: List[str]
    model_version: str = SCORING_MODEL_VERSION


ROLE_MATRIX: Dict[RoleType, Dict[RoleType, float]] = {
    "builder":    {"builder": 50, "seller": 100, "operator": 85, "researcher": 80},
    "seller":     {"builder": 100, "seller": 50, "operator": 80, "researcher": 75},
    "operator":   {"builder": 85, "seller": 80, "operator": 50, "researcher": 70},
    "researcher": {"builder": 80, "seller": 75, "operator": 70, "researcher": 50},
}

GOAL_MATRIX: Dict[IntentGoal, Dict[IntentGoal, float]] = {
    "build_company":    {"build_company": 100, "try_idea": 70,  "gain_experience": 60, "stable_income": 10},
    "try_idea":         {"build_company": 70,  "try_idea": 100, "gain_experience": 60, "stable_income": 10},
    "gain_experience":  {"build_company": 60,  "try_idea": 60,  "gain_experience": 100,"stable_income": 20},
    "stable_income":    {"build_company": 10,  "try_idea": 10,  "gain_experience": 20, "stable_income": 100},
}

CONFLICT_MATRIX: Dict[ConflictStyle, Dict[ConflictStyle, float]] = {
    "calm_discussion": {"calm_discussion": 90, "depends": 80, "avoid": 70, "direct_clash": 65},
    "depends":         {"calm_discussion": 80, "depends": 75, "avoid": 65, "direct_clash": 60},
    "avoid":           {"calm_discussion": 70, "depends": 65, "avoid": 40, "direct_clash": 50},
    "direct_clash":    {"calm_discussion": 65, "depends": 60, "avoid": 50, "direct_clash": 50},
}

WORK_MODE_MATRIX: Dict[WorkMode, Dict[WorkMode, float]] = {
    "tight_pair": {"tight_pair": 95, "any": 90, "team": 75, "solo": 55},
    "any":        {"tight_pair": 90, "any": 80, "team": 75, "solo": 65},
    "team":       {"tight_pair": 75, "any": 75, "team": 80, "solo": 60},
    "solo":       {"tight_pair": 55, "any": 65, "team": 60, "solo": 40},
}

DECISION_VALUES: Dict[DecisionStyle, float] = {
    "fast_risky": 0, "analyze_first": 40, "discuss_first": 70, "delay_until_clear": 100,
}


def clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, round(v, 2)))

def linear_pair(v1: float, v2: float, mult: float = 1.0) -> float:
    return clamp(100 - abs(v1 - v2) * mult)

def intent_score(a: FounderProfile, b: FounderProfile) -> float:
    return clamp(0.4*linear_pair(a.time_commitment, b.time_commitment, 2.0)
               + 0.3*linear_pair(a.no_salary_readiness, b.no_salary_readiness, 1.5)
               + 0.3*GOAL_MATRIX[a.intent_goal][b.intent_goal])

def role_score(a: FounderProfile, b: FounderProfile) -> float:
    s = ROLE_MATRIX[a.primary_role][b.primary_role]
    if b.primary_role in a.no_go_roles: s -= 30
    if a.primary_role in b.no_go_roles: s -= 30
    if a.primary_role == b.primary_role: s -= 5
    return clamp(s)

def _tempo_pair(a: TempoType, b: TempoType) -> float:
    if a == b == "iterate_fast": return 80
    if a == b == "build_right_first": return 70
    return 20

def tempo_score(a: FounderProfile, b: FounderProfile) -> float:
    return clamp(0.6*_tempo_pair(a.tempo, b.tempo)
               + 0.4*linear_pair(a.sync_frequency, b.sync_frequency, 1.5))

def work_style_score(a: FounderProfile, b: FounderProfile) -> float:
    dp = linear_pair(DECISION_VALUES[a.decision_style], DECISION_VALUES[b.decision_style])
    if a.decision_style == b.decision_style == "delay_until_clear": dp = min(dp, 40)
    return clamp(0.4*dp
               + 0.3*CONFLICT_MATRIX[a.conflict_style][b.conflict_style]
               + 0.3*WORK_MODE_MATRIX[a.work_mode][b.work_mode])

def accountability_score(a: FounderProfile, b: FounderProfile) -> float:
    floor = min(a.accountability_disappear, b.accountability_disappear,
                a.accountability_ownership, b.accountability_ownership)
    return clamp(0.3*linear_pair(a.accountability_disappear, b.accountability_disappear)
               + 0.3*linear_pair(a.accountability_ownership, b.accountability_ownership)
               + 0.4*floor)

def experience_score(a: FounderProfile, b: FounderProfile) -> float:
    return clamp(0.6*linear_pair(a.launched_projects, b.launched_projects, 0.8)
               + 0.4*linear_pair(a.self_execution_breadth, b.self_execution_breadth, 0.7))

def _founder_fit(a: FounderProfile, b: FounderProfile):
    s = {
        "intent_score":         intent_score(a, b),
        "role_score":           role_score(a, b),
        "tempo_score":          tempo_score(a, b),
        "work_style_score":     work_style_score(a, b),
        "accountability_score": accountability_score(a, b),
        "experience_score":     experience_score(a, b),
    }
    ff = clamp(0.25*s["intent_score"] + 0.20*s["role_score"] + 0.20*s["tempo_score"]
             + 0.15*s["work_style_score"] + 0.15*s["accountability_score"] + 0.05*s["experience_score"])
    s["founder_fit_score"] = ff
    return s, ff

def _c_pair(c1, c2):
    d = abs(c1-c2); s = 100-d
    if d > 55: s -= 20
    elif d > 35: s -= 10
    return clamp(s)

def _a_pair(a1, a2):
    return clamp(0.6*min(a1,a2) + 0.4*(100-abs(a1-a2)))

def _es_pair(e1, e2):
    s = 0.7*min(e1,e2) + 0.3*(100-abs(e1-e2))
    if e1 < 35 and e2 < 35: s -= 15
    return clamp(s)

def _e_bonus(a: FounderProfile, b: FounderProfile) -> float:
    rs = {a.primary_role, b.primary_role}
    ok = bool(rs & {"seller","operator"}) and bool(rs & {"builder","researcher"})
    d = abs(a.big5.extraversion - b.big5.extraversion)  # type: ignore
    return 10 if ok and 15 <= d <= 45 else 0

def big5_scores(a: FounderProfile, b: FounderProfile) -> Dict[str, float]:
    if not a.big5 or not b.big5: return {}
    o  = clamp(0.5*(100-abs(a.big5.openness-b.big5.openness)) + 0.5*((a.big5.openness+b.big5.openness)/2))
    c  = _c_pair(a.big5.conscientiousness, b.big5.conscientiousness)
    e  = clamp(70 - 0.4*abs(a.big5.extraversion-b.big5.extraversion) + _e_bonus(a,b))
    ag = _a_pair(a.big5.agreeableness, b.big5.agreeableness)
    es = _es_pair(a.big5.emotional_stability, b.big5.emotional_stability)
    total = clamp(0.10*o + 0.30*c + 0.15*e + 0.20*ag + 0.25*es)
    return {"big5_openness_score": o, "big5_conscientiousness_score": c,
            "big5_extraversion_score": e, "big5_agreeableness_score": ag,
            "big5_emotional_stability_score": es, "big5_fit_score": total}

def build_risk_flags(a: FounderProfile, b: FounderProfile, scores: Dict) -> List[str]:
    flags = []
    if scores["intent_score"] < 40:          flags.append("low_intent_alignment")
    if scores["accountability_score"] < 35:  flags.append("low_accountability_alignment")
    if scores["tempo_score"] < 40:           flags.append("tempo_conflict")
    if a.primary_role == b.primary_role:     flags.append("same_primary_role")
    if a.big5 and b.big5:
        if a.big5.emotional_stability < 35 and b.big5.emotional_stability < 35:
            flags.append("high_emotional_volatility")
        if abs(a.big5.conscientiousness - b.big5.conscientiousness) > 40:
            flags.append("execution_style_gap")
        if min(a.big5.agreeableness, b.big5.agreeableness) < 30:
            flags.append("low_cooperation_risk")
    return flags

def score_pair(a: FounderProfile, b: FounderProfile) -> ScoreBreakdown:
    """Основная точка входа. Симметрична: score_pair(a,b) == score_pair(b,a)."""
    scores, ff = _founder_fit(a, b)
    b5 = big5_scores(a, b)
    scores.update(b5)
    scores["total_compatibility_score"] = clamp(0.80*ff + 0.20*b5["big5_fit_score"]) if b5 else ff
    scores["risk_flags"] = build_risk_flags(a, b, scores)
    return ScoreBreakdown(**scores)


def score_pair_with_mystic(
    profile_a: FounderProfile,
    profile_b: FounderProfile,
    mystic_a: Optional[Dict] = None,
    mystic_b: Optional[Dict] = None,
) -> Dict:
    """
    Расширенный scoring: FounderFit + Mystic (MBTI / эннеаграмма).

    Формула:
      total = 0.75 * founder_fit + 0.25 * mystic_total   (если mystic доступен)
      total = founder_fit                                (иначе — прежняя формула)

    `mystic_a` / `mystic_b` — `normalized_profile` dict'ы (с ключами
    `mbti_type` / `enneagram_type`). Если любой не передан — mystic не применяется.
    """
    from core.mystic.analysis import compute_mystic_score  # локальный импорт — избегаем цикла

    base = score_pair(profile_a, profile_b)
    founder_fit = base.founder_fit_score

    if mystic_a is None or mystic_b is None:
        return {
            "founder_fit_score": founder_fit,
            "mystic": None,
            "total_score": base.total_compatibility_score,
            "breakdown": base.model_dump(),
        }

    mystic = compute_mystic_score(mystic_a, mystic_b)
    total = clamp(0.75 * founder_fit + 0.25 * mystic["mystic_total"])

    return {
        "founder_fit_score": founder_fit,
        "mystic": mystic,
        "total_score": total,
        "breakdown": base.model_dump(),
    }

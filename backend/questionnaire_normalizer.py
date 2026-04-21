"""
SyndiAI Founder Matching — Questionnaire Normalizer
Version: syndiai-onboarding-schema-v0.1

Переводит raw ответы онбординга + Big Five Likert в нормализованный FounderProfile.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from scoring import (
    BigFiveProfile, ConflictStyle, DecisionStyle,
    FounderProfile, IntentGoal, RoleType, TempoType, WorkMode,
)

ONBOARDING_SCHEMA_VERSION = "syndiai-onboarding-schema-v0.1"

BIG5_REVERSE_MASKS: Dict[str, List[bool]] = {
    "openness":            [False, False, True,  False],
    "conscientiousness":   [False, False, False, True],
    "extraversion":        [False, True,  False, False],
    "agreeableness":       [False, False, True,  False],
    "emotional_stability": [True,  True,  False, False],  # es1=neuroticism(R), es2=neuroticism(R), es3=stability, es4=stability
}

def _scale(v: float, mn: float, mx: float) -> float:
    if mx == mn: return 0.0
    return round(max(0.0, min(100.0, (v - mn) / (mx - mn) * 100)), 2)

def _likert(v: int, reverse: bool = False) -> float:
    s = (max(1, min(5, v)) - 1) / 4 * 100
    return round(100 - s if reverse else s, 2)

def _avg_likert(vals: List[int], revs: Optional[List[bool]] = None) -> float:
    if revs is None: revs = [False] * len(vals)
    return round(sum(_likert(v, r) for v, r in zip(vals, revs)) / len(vals), 2)

def normalize_big5(raw: Optional[Dict[str, List[int]]]) -> Optional[BigFiveProfile]:
    if not raw: return None
    traits = {}
    for trait, revs in BIG5_REVERSE_MASKS.items():
        vals = raw.get(trait)
        if not vals: return None
        traits[trait] = _avg_likert(vals, revs)
    return BigFiveProfile(**traits)

def normalize(raw: Dict[str, Any]) -> FounderProfile:
    """
    Точка входа для OnboardingService.
    raw — словарь из POST /api/v1/onboarding/submit.

    Ожидаемые поля:
      user_id, time_commitment_hours_per_week (0-80),
      no_salary_readiness_months (0-24), intent_goal, launched_projects_count (0-10),
      self_execution_breadth (0-10), primary_role, no_go_roles[], decision_style,
      conflict_style, work_mode, tempo, sync_frequency_per_week (0-7),
      accountability_disappear_risk (Likert 1-5, высокий=плохо),
      accountability_ownership_drive (Likert 1-5, высокий=хорошо),
      big5: {openness, conscientiousness, extraversion, agreeableness, emotional_stability}
            каждый — список из 4 Likert-ответов
    """
    return FounderProfile(
        user_id=str(raw["user_id"]),
        time_commitment=_scale(float(raw.get("time_commitment_hours_per_week", 0)), 0, 80),
        no_salary_readiness=_scale(float(raw.get("no_salary_readiness_months", 0)), 0, 24),
        intent_goal=raw["intent_goal"],
        launched_projects=_scale(float(raw.get("launched_projects_count", 0)), 0, 10),
        self_execution_breadth=_scale(float(raw.get("self_execution_breadth", 0)), 0, 10),
        primary_role=raw["primary_role"],
        no_go_roles=raw.get("no_go_roles", []),
        decision_style=raw["decision_style"],
        conflict_style=raw["conflict_style"],
        work_mode=raw["work_mode"],
        tempo=raw["tempo"],
        sync_frequency=_scale(float(raw.get("sync_frequency_per_week", 0)), 0, 7),
        accountability_disappear=_likert(int(raw.get("accountability_disappear_risk", 3)), reverse=True),
        accountability_ownership=_likert(int(raw.get("accountability_ownership_drive", 3))),
        big5=normalize_big5(raw.get("big5")),
    )

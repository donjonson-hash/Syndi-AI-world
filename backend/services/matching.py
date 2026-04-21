"""
SyndiAI Matching Service — адаптер поверх scoring.py
Заменяет старый MatchingEngine. Интерфейс backward-compatible с main.py.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from services.scoring import FounderProfile, ScoreBreakdown, score_pair
from services.questionnaire_normalizer import normalize


class MatchResult:
    """Результат матча — совместим со старым интерфейсом + расширен."""

    def __init__(
        self,
        candidate_id: str,
        candidate_name: str,
        breakdown: ScoreBreakdown,
    ):
        self.candidate_id   = candidate_id
        self.candidate_name = candidate_name
        self.breakdown      = breakdown
        self.score          = breakdown.total_compatibility_score

    @property
    def overall_score(self) -> float:
        return self.score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id":           self.candidate_id,
            "candidate_name":         self.candidate_name,
            "total_compatibility":    round(self.score, 2),
            "founder_fit_score":      self.breakdown.founder_fit_score,
            "big5_fit_score":         self.breakdown.big5_fit_score,
            "risk_flags":             self.breakdown.risk_flags,
            "model_version":          self.breakdown.model_version,
            "breakdown": {
                "intent":         self.breakdown.intent_score,
                "role":           self.breakdown.role_score,
                "tempo":          self.breakdown.tempo_score,
                "work_style":     self.breakdown.work_style_score,
                "accountability": self.breakdown.accountability_score,
                "experience":     self.breakdown.experience_score,
            },
        }


class MatchingService:
    """
    Сервис матчинга.

    Использование:
        service = MatchingService()
        results = service.match_founder(my_raw_answers, [candidate1_raw, candidate2_raw])
        top = service.get_shortlist(results, limit=3)
    """

    def match_founder(
        self,
        requester_raw: Dict[str, Any],
        candidates_raw: List[Dict[str, Any]],
    ) -> List[MatchResult]:
        """
        Считает совместимость requester со всеми кандидатами.
        requester_raw и candidates_raw — сырые ответы онбординга.
        """
        requester = normalize(requester_raw)
        results: List[MatchResult] = []
        for raw in candidates_raw:
            candidate = normalize(raw)
            breakdown = score_pair(requester, candidate)
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                candidate_name=str(raw.get("name", candidate.user_id)),
                breakdown=breakdown,
            ))
        return results

    def match_profiles(
        self,
        requester: FounderProfile,
        candidates: List[FounderProfile],
        names: Optional[Dict[str, str]] = None,
    ) -> List[MatchResult]:
        """
        Принимает уже нормализованные FounderProfile (для прямого вызова из БД).
        names: {user_id: display_name}
        """
        names = names or {}
        results: List[MatchResult] = []
        for candidate in candidates:
            breakdown = score_pair(requester, candidate)
            results.append(MatchResult(
                candidate_id=candidate.user_id,
                candidate_name=names.get(candidate.user_id, candidate.user_id),
                breakdown=breakdown,
            ))
        return results

    @staticmethod
    def get_shortlist(results: List[MatchResult], limit: int = 3) -> List[MatchResult]:
        return sorted(results, key=lambda r: r.score, reverse=True)[:limit]

    @staticmethod
    def filter_by_risk(
        results: List[MatchResult],
        exclude_flags: Optional[List[str]] = None,
    ) -> List[MatchResult]:
        """Убирает матчи с указанными risk_flags."""
        if not exclude_flags:
            return results
        return [r for r in results if not any(f in r.breakdown.risk_flags for f in exclude_flags)]

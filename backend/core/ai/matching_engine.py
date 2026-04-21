"""
MatchingEngine — legacy wrapper.
Реальная логика перенесена в services/scoring.py и services/matching.py.
Этот файл сохранён для backward compatibility с импортами в main.py.
"""
from services.matching import MatchingService, MatchResult  # noqa: F401

class MatchingEngine(MatchingService):
    """
    Алиас MatchingService.
    Используй MatchingService напрямую для новых интеграций.
    """
    pass

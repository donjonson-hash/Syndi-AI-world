"""
Matching Service for Syndi-AI
"""
from typing import List, Dict, Any, Optional, Tuple
from models.user import UserProfile, UserGoal
from models.big_five import BigFiveProfile


class MatchResult:
    def __init__(self, user, score: float, reasons: List[str]):
        self.user = user
        self.score = score
        self.reasons = reasons
    
    @property
    def overall_score(self) -> float:
        """ДОБАВИТЬ ЭТОТ PROPERTY"""
        return self.score


class MatchingEngine:
    def __init__(self):
        self.weights = {
            "skills": 0.40,
            "personality": 0.35,
            "goals": 0.25
        }
    
    def calculate_compatibility(self, user1, user2) -> float:
        skills_score = self._calculate_skills_match(user1, user2)
        personality_score = self._calculate_personality_match(user1, user2)
        goals_score = self._calculate_goals_match(user1, user2)
        # Возвращаем в масштабе 0-100
        return round(
            (skills_score * self.weights["skills"] +
            personality_score * self.weights["personality"] +
            goals_score * self.weights["goals"]),
            2
        )
    
    def _calculate_skills_match(self, user1, user2) -> float:
        if not hasattr(user1, 'skills') or not hasattr(user2, 'skills'):
            return 50.0
        if not user1.skills or not user2.skills:
            return 50.0
        set1 = set(s.name for s in user1.skills)
        set2 = set(s.name for s in user2.skills)
        total = len(set1 | set2)
        if total == 0:
            return 50.0
        unique = len(set1 - set2) + len(set2 - set1)
        return (0.3 + (unique / total) * 0.7) * 100
    
    def _calculate_personality_match(self, user1, user2) -> float:
        p1 = getattr(user1, 'big_five', user1)
        p2 = getattr(user2, 'big_five', user2)
        
        if p1 is None or p2 is None:
            return 50.0
        
        if hasattr(p1, 'openness'):
            scores = [
                1 - abs(p1.openness - p2.openness) / 100,
                1 - abs(p1.conscientiousness - p2.conscientiousness) / 100,
                0.5 + 0.5 * abs(p1.extraversion - p2.extraversion) / 100,
                1 - abs(p1.agreeableness - p2.agreeableness) / 100,
                1 - (p1.neuroticism + p2.neuroticism) / 200,
            ]
            return (sum(scores) / len(scores)) * 100
        return 50.0
    
    def _calculate_goals_match(self, user1, user2) -> float:
        g1 = getattr(user1, 'goals', user1)
        g2 = getattr(user2, 'goals', user2)
        
        if not g1 or not g2:
            return 50.0
        
        set1 = set(g1) if isinstance(g1, list) else set()
        set2 = set(g2) if isinstance(g2, list) else set()
        
        if not set1 or not set2:
            return 50.0
        
        # Преобразуем цели в строки для сравнения
        def goal_to_str(g):
            if hasattr(g, 'value'):
                return g.value.lower()
            return str(g).lower().replace('usergoal.', '')
        
        set1_str = {goal_to_str(g) for g in set1}
        set2_str = {goal_to_str(g) for g in set2}
        
        # Если одинаковые цели - 100%
        intersection = set1_str & set2_str
        if intersection:
            return 100.0
        
        # Проверяем совместимость целей
        # find_cofounder совместим с join_project
        if ('find_cofounder' in set1_str and 'join_project' in set2_str) or \
           ('join_project' in set1_str and 'find_cofounder' in set2_str):
            return 75.0
        
        # hire_talent совместим с find_team
        if ('hire_talent' in set1_str and 'find_team' in set2_str) or \
           ('find_team' in set1_str and 'hire_talent' in set2_str):
            return 75.0
        
        # networking с networking
        if 'networking' in set1_str and 'networking' in set2_str:
            return 100.0
        
        # mentorship с любой другой целью (кроме уже проверенных)
        if 'mentorship' in set1_str or 'mentorship' in set2_str:
            return 50.0
        
        return 0.0
    
    def find_matches(self, user, candidates, limit: int = 10) -> List[MatchResult]:
        results = []
        for candidate in candidates:
            if str(getattr(candidate, 'id', None)) == str(getattr(user, 'id', None)):
                continue
            score = self.calculate_compatibility(user, candidate)
            reasons = self._generate_reasons(user, candidate)
            results.append(MatchResult(candidate, score, reasons))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def _generate_reasons(self, user1, user2) -> List[str]:
        reasons = []
        if hasattr(user1, 'skills') and hasattr(user2, 'skills'):
            set1 = set(s.name for s in user1.skills)
            set2 = set(s.name for s in user2.skills)
            unique = set2 - set1
            if unique:
                reasons.append(f"Дополняет навыками: {', '.join(list(unique)[:3])}")
        return reasons or ["Хорошая совместимость"]
    
    # Алиасы для тестов
    def _calculate_skill_match(self, skills1, skills2) -> Tuple[float, List[str]]:
        """Алиас для тестов - возвращает (score, complementary_skills)"""
        class FakeUser:
            def __init__(self, skills):
                self.skills = skills
        score = self._calculate_skills_match(FakeUser(skills1), FakeUser(skills2))
        
        # Вычисляем complementary skills
        set1 = set(s.name for s in skills1) if skills1 else set()
        set2 = set(s.name for s in skills2) if skills2 else set()
        complementary = list(set2 - set1)
        
        return score, complementary
    
    def _calculate_goal_match(self, goals1, goals2) -> float:
        """Алиас для тестов"""
        class FakeUser:
            def __init__(self, goals):
                self.goals = goals
        return self._calculate_goals_match(FakeUser(goals1), FakeUser(goals2))


class QuickMatcher:
    @staticmethod
    def quick_match(user, candidates: List, limit: int = 5) -> List[MatchResult]:
        """Исправлено: limit=5 по умолчанию"""
        engine = MatchingEngine()
        results = []
        for candidate in candidates:
            score = engine.calculate_compatibility(user, candidate)
            results.append(MatchResult(candidate, score, ["Совместимость"]))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

"""
Matching Algorithm
Алгоритм матчинга пользователей на основе навыков и психотипа
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import math

from models.user import UserProfile, Skill, UserGoal, UserPublicProfile
from models.big_five import BigFiveProfile


@dataclass
class MatchResult:
    """Результат матчинга"""
    user: UserPublicProfile
    overall_score: float  # 0-100
    skill_score: float    # 0-100
    personality_score: float  # 0-100
    goal_score: float     # 0-100
    complementary_skills: List[str]  # Навыки, которые дополняют друг друга
    shared_interests: List[str]  # Общие интересы
    
    def to_dict(self) -> Dict:
        return {
            "user": {
                "id": str(self.user.id),
                "name": self.user.name,
                "title": self.user.title,
                "bio": self.user.bio,
                "location": self.user.location,
                "skills": [s.dict() for s in self.user.skills],
                "goals": [g.value for g in self.user.goals],
                "interests": self.user.interests,
                "big_five": self.user.big_five.to_dict() if self.user.big_five else None
            },
            "scores": {
                "overall": round(self.overall_score, 1),
                "skill": round(self.skill_score, 1),
                "personality": round(self.personality_score, 1),
                "goal": round(self.goal_score, 1)
            },
            "complementary_skills": self.complementary_skills,
            "shared_interests": self.shared_interests
        }


class MatchingEngine:
    """
    Движок матчинга Syndi
    
    Алгоритм учитывает:
    1. Совместимость навыков (комплементарность)
    2. Совместимость личности (Big Five)
    3. Совместимость целей
    4. Географическую близость (опционально)
    """
    
    def __init__(
        self,
        skill_weight: float = 0.4,
        personality_weight: float = 0.35,
        goal_weight: float = 0.25
    ):
        self.skill_weight = skill_weight
        self.personality_weight = personality_weight
        self.goal_weight = goal_weight
    
    def find_matches(
        self,
        user: UserProfile,
        candidates: List[UserProfile],
        limit: int = 10,
        min_score: float = 50.0
    ) -> List[MatchResult]:
        """
        Находит лучшие совпадения для пользователя
        
        Args:
            user: Текущий пользователь
            candidates: Список кандидатов для матчинга
            limit: Максимальное количество результатов
            min_score: Минимальный общий балл для включения
        
        Returns:
            Список MatchResult, отсортированный по overall_score
        """
        results = []
        
        for candidate in candidates:
            if candidate.id == user.id:
                continue
            
            match = self._calculate_match(user, candidate)
            if match.overall_score >= min_score:
                results.append(match)
        
        # Сортируем по общему баллу (убывание)
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return results[:limit]
    
    def _calculate_match(
        self,
        user1: UserProfile,
        user2: UserProfile
    ) -> MatchResult:
        """Вычисляет совместимость двух пользователей"""
        
        # 1. Оценка навыков
        skill_score, complementary = self._calculate_skill_match(
            user1.skills, user2.skills
        )
        
        # 2. Оценка личности
        personality_score = self._calculate_personality_match(
            user1.big_five, user2.big_five
        )
        
        # 3. Оценка целей
        goal_score = self._calculate_goal_match(
            user1.goals, user2.goals
        )
        
        # 4. Общий балл (взвешенное среднее)
        overall_score = (
            skill_score * self.skill_weight +
            personality_score * self.personality_weight +
            goal_score * self.goal_weight
        )
        
        # 5. Общие интересы
        shared_interests = list(
            set(user1.interests) & set(user2.interests)
        )
        
        # Создаём публичный профиль для ответа
        public_profile = UserPublicProfile(
            id=user2.id,
            name=user2.name,
            avatar_url=user2.avatar_url,
            title=user2.title,
            bio=user2.bio,
            location=user2.location,
            skills=user2.skills,
            goals=user2.goals,
            interests=user2.interests,
            big_five=user2.big_five,
            compatibility_score=overall_score
        )
        
        return MatchResult(
            user=public_profile,
            overall_score=overall_score,
            skill_score=skill_score,
            personality_score=personality_score,
            goal_score=goal_score,
            complementary_skills=complementary,
            shared_interests=shared_interests
        )
    
    def _calculate_skill_match(
        self,
        skills1: List[Skill],
        skills2: List[Skill]
    ) -> Tuple[float, List[str]]:
        """
        Вычисляет совместимость навыков
        
        Логика: ищем комплементарность (разные, но совместимые навыки)
        а не просто совпадение
        
        Returns:
            (score, complementary_skills)
        """
        if not skills1 or not skills2:
            return 50.0, []
        
        # Создаём словари навыков
        skills1_dict = {s.name.lower(): s for s in skills1}
        skills2_dict = {s.name.lower(): s for s in skills2}
        
        all_skills = set(skills1_dict.keys()) | set(skills2_dict.keys())
        shared_skills = set(skills1_dict.keys()) & set(skills2_dict.keys())
        
        # Навыки, которыми владеет только один из пользователей
        unique_to_user2 = set(skills2_dict.keys()) - set(skills1_dict.keys())
        unique_to_user1 = set(skills1_dict.keys()) - set(skills2_dict.keys())
        
        # Комплементарные навыки (то, что может предложить каждый)
        complementary = list(unique_to_user2)
        
        # Расчёт оценки
        if not all_skills:
            return 50.0, []
        
        # 1. Небольшой бонус за общие навыки (совместное понимание)
        shared_bonus = len(shared_skills) / len(all_skills) * 20
        
        # 2. Основной балл - за комплементарность
        # Чем больше уникальных навыков у обоих, тем лучше
        complementarity = (len(unique_to_user1) + len(unique_to_user2)) / len(all_skills)
        complement_score = complementarity * 80
        
        score = min(100, shared_bonus + complement_score)
        
        return score, complementary[:5]  # Возвращаем топ-5 комплементарных навыков
    
    def _calculate_personality_match(
        self,
        profile1: Optional[BigFiveProfile],
        profile2: Optional[BigFiveProfile]
    ) -> float:
        """
        Вычисляет совместимость личностей по Big Five
        
        Если профиль отсутствует, возвращает нейтральную оценку
        """
        if not profile1 or not profile2:
            return 50.0  # Нейтральная оценка без теста
        
        return profile1.compatibility_score(profile2)
    
    def _calculate_goal_match(
        self,
        goals1: List[UserGoal],
        goals2: List[UserGoal]
    ) -> float:
        """
        Вычисляет совместимость целей
        
        Некоторые цели хорошо сочетаются:
        - FIND_COFOUNDER ↔ JOIN_PROJECT
        - FIND_TEAM ↔ JOIN_PROJECT
        - HIRE_TALENT ↔ JOIN_PROJECT
        """
        if not goals1 or not goals2:
            return 50.0
        
        # Совместимые пары целей
        compatible_pairs = {
            (UserGoal.FIND_COFOUNDER, UserGoal.JOIN_PROJECT),
            (UserGoal.JOIN_PROJECT, UserGoal.FIND_COFOUNDER),
            (UserGoal.FIND_TEAM, UserGoal.JOIN_PROJECT),
            (UserGoal.JOIN_PROJECT, UserGoal.FIND_TEAM),
            (UserGoal.HIRE_TALENT, UserGoal.JOIN_PROJECT),
            (UserGoal.JOIN_PROJECT, UserGoal.HIRE_TALENT),
            (UserGoal.MENTORSHIP, UserGoal.JOIN_PROJECT),
            (UserGoal.JOIN_PROJECT, UserGoal.MENTORSHIP),
        }
        
        # Подсчитываем совпадения и совместимости
        matches = 0
        for g1 in goals1:
            for g2 in goals2:
                if g1 == g2:
                    matches += 1
                elif (g1, g2) in compatible_pairs:
                    matches += 0.8
        
        max_possible = max(len(goals1), len(goals2))
        if max_possible == 0:
            return 50.0
        
        score = (matches / max_possible) * 100
        return min(100, score)


class QuickMatcher:
    """
    Быстрый матчер для MVP (без сложных вычислений)
    
    Использует упрощённый алгоритм для быстрого прототипирования
    """
    
    @staticmethod
    def quick_match(
        user: UserProfile,
        candidates: List[UserProfile]
    ) -> List[MatchResult]:
        """Упрощённый матчинг для MVP"""
        
        engine = MatchingEngine(
            skill_weight=0.5,
            personality_weight=0.3,
            goal_weight=0.2
        )
        
        return engine.find_matches(user, candidates, limit=5, min_score=30)


# Примеры совместимости психотипов для рекомендаций
PERSONALITY_COMPATIBILITY_GUIDE = {
    "high_openness": "Отлично подходят для инновационных проектов и стартапов",
    "high_conscientiousness": "Надёжные исполнители, хорошо справляются с дедлайнами",
    "high_extraversion": "Идеальны для ролей, связанных с коммуникацией и продажами",
    "high_agreeableness": "Отличные командные игроки, создают гармонию в коллективе",
    "low_neuroticism": "Сохраняют спокойствие в кризисных ситуациях",
    "complementary_skills": "Разные навыки создают сильную команду",
    "similar_goals": "Общие цели увеличивают шансы на успех проекта"
}

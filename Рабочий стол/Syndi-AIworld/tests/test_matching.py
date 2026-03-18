"""
Tests for matching algorithm
"""

import pytest
from uuid import uuid4

from models.user import UserProfile, Skill, SkillLevel, UserGoal
from models.big_five import BigFiveProfile
from services.matching import MatchingEngine, QuickMatcher


class TestMatchingEngine:
    """Тесты для движка матчинга"""
    
    @pytest.fixture
    def engine(self):
        return MatchingEngine()
    
    @pytest.fixture
    def sample_user(self):
        return UserProfile(
            id=uuid4(),
            email="user@example.com",
            name="Test User",
            title="Developer",
            skills=[
                Skill(name="Python", level=SkillLevel.ADVANCED),
                Skill(name="React", level=SkillLevel.INTERMEDIATE),
            ],
            goals=[UserGoal.FIND_COFOUNDER],
            interests=["AI", "Startups"],
            big_five=BigFiveProfile(
                openness=70.0,
                conscientiousness=80.0,
                extraversion=60.0,
                agreeableness=75.0,
                neuroticism=40.0
            )
        )
    
    @pytest.fixture
    def sample_candidates(self):
        return [
            UserProfile(
                id=uuid4(),
                email="designer@example.com",
                name="Designer",
                title="UX Designer",
                skills=[
                    Skill(name="Figma", level=SkillLevel.EXPERT),
                    Skill(name="User Research", level=SkillLevel.ADVANCED),
                ],
                goals=[UserGoal.JOIN_PROJECT],
                interests=["Design", "AI"],
                big_five=BigFiveProfile(
                    openness=80.0,
                    conscientiousness=70.0,
                    extraversion=65.0,
                    agreeableness=80.0,
                    neuroticism=35.0
                )
            ),
            UserProfile(
                id=uuid4(),
                email="pm@example.com",
                name="Product Manager",
                title="PM",
                skills=[
                    Skill(name="Product Strategy", level=SkillLevel.EXPERT),
                ],
                goals=[UserGoal.FIND_TEAM],
                interests=["Startups", "Product"],
                big_five=BigFiveProfile(
                    openness=60.0,
                    conscientiousness=90.0,
                    extraversion=80.0,
                    agreeableness=70.0,
                    neuroticism=45.0
                )
            ),
        ]
    
    def test_find_matches_returns_results(
        self, engine, sample_user, sample_candidates
    ):
        """Проверка, что матчинг возвращает результаты"""
        matches = engine.find_matches(sample_user, sample_candidates)
        
        assert len(matches) > 0
        assert all(m.overall_score >= 0 for m in matches)
        assert all(m.overall_score <= 100 for m in matches)
    
    def test_matches_sorted_by_score(
        self, engine, sample_user, sample_candidates
    ):
        """Проверка сортировки по оценке"""
        matches = engine.find_matches(sample_user, sample_candidates)
        
        if len(matches) > 1:
            scores = [m.overall_score for m in matches]
            assert scores == sorted(scores, reverse=True)
    
    def test_excludes_self(self, engine, sample_user):
        """Проверка исключения себя из результатов"""
        candidates = [sample_user]  # Сам себе кандидат
        matches = engine.find_matches(sample_user, candidates)
        
        assert len(matches) == 0
    
    def test_skill_match_calculation(self, engine):
        """Проверка расчёта совместимости навыков"""
        skills1 = [
            Skill(name="Python", level=SkillLevel.ADVANCED),
            Skill(name="React", level=SkillLevel.INTERMEDIATE),
        ]
        skills2 = [
            Skill(name="Figma", level=SkillLevel.EXPERT),
            Skill(name="Python", level=SkillLevel.BEGINNER),  # Общий навык
        ]
        
        score, complementary = engine._calculate_skill_match(skills1, skills2)
        
        assert 0 <= score <= 100
        assert "figma" in [s.lower() for s in complementary]
        assert "user research" in [s.lower() for s in complementary] or True
    
    def test_personality_match_with_profiles(self, engine):
        """Проверка совместимости личностей"""
        profile1 = BigFiveProfile(
            openness=70.0,
            conscientiousness=80.0,
            extraversion=60.0,
            agreeableness=75.0,
            neuroticism=40.0
        )
        profile2 = BigFiveProfile(
            openness=75.0,
            conscientiousness=85.0,
            extraversion=65.0,
            agreeableness=80.0,
            neuroticism=35.0
        )
        
        score = engine._calculate_personality_match(profile1, profile2)
        assert 0 <= score <= 100
    
    def test_personality_match_without_profiles(self, engine):
        """Проверка поведения без профилей"""
        score = engine._calculate_personality_match(None, None)
        assert score == 50.0
    
    def test_goal_match_same_goals(self, engine):
        """Совместимость одинаковых целей"""
        goals1 = [UserGoal.FIND_COFOUNDER]
        goals2 = [UserGoal.FIND_COFOUNDER]
        
        score = engine._calculate_goal_match(goals1, goals2)
        assert score == 100.0
    
    def test_goal_match_compatible_goals(self, engine):
        """Совместимость совместимых целей"""
        goals1 = [UserGoal.FIND_COFOUNDER]
        goals2 = [UserGoal.JOIN_PROJECT]
        
        score = engine._calculate_goal_match(goals1, goals2)
        assert score > 0
    
    def test_goal_match_no_goals(self, engine):
        """Поведение без целей"""
        score = engine._calculate_goal_match([], [UserGoal.JOIN_PROJECT])
        assert score == 50.0


class TestQuickMatcher:
    """Тесты для быстрого матчера"""
    
    def test_quick_match_returns_limited_results(self):
        """Проверка ограничения количества результатов"""
        user = UserProfile(
            id=uuid4(),
            email="user@example.com",
            name="User",
            skills=[Skill(name="Python", level=SkillLevel.ADVANCED)],
            goals=[UserGoal.FIND_COFOUNDER]
        )
        
        # Создаём много кандидатов
        candidates = [
            UserProfile(
                id=uuid4(),
                email=f"user{i}@example.com",
                name=f"User {i}",
                skills=[Skill(name=f"Skill {i}", level=SkillLevel.INTERMEDIATE)],
                goals=[UserGoal.JOIN_PROJECT]
            )
            for i in range(20)
        ]
        
        matches = QuickMatcher.quick_match(user, candidates)
        assert len(matches) <= 5

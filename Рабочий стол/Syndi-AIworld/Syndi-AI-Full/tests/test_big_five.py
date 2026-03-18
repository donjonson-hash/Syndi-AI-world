"""
Tests for Big Five personality assessment
"""

import pytest
from models.big_five import (
    BigFiveTest, BigFiveProfile, TraitType, 
    AnswerScale, BIG_FIVE_QUESTIONS
)


class TestBigFiveTest:
    """Тесты для теста Big Five"""
    
    def test_get_questions(self):
        """Проверка получения списка вопросов"""
        test = BigFiveTest()
        questions = test.get_questions()
        
        assert len(questions) == 15
        assert all("id" in q for q in questions)
        assert all("text" in q for q in questions)
        assert all("trait" in q for q in questions)
    
    def test_calculate_profile_all_high(self):
        """Тест с максимальными ответами (все 5)"""
        test = BigFiveTest()
        
        # Все ответы = 5 (кроме обратных вопросов)
        answers = {i: 5 for i in range(1, 16)}
        profile = test.calculate_profile(answers)
        
        # Проверяем, что значения в диапазоне 0-100
        assert 0 <= profile.openness <= 100
        assert 0 <= profile.conscientiousness <= 100
        assert 0 <= profile.extraversion <= 100
        assert 0 <= profile.agreeableness <= 100
        assert 0 <= profile.neuroticism <= 100
    
    def test_calculate_profile_all_low(self):
        """Тест с минимальными ответами (все 1)"""
        test = BigFiveTest()
        
        # Все ответы = 1
        answers = {i: 1 for i in range(1, 16)}
        profile = test.calculate_profile(answers)
        
        # Проверяем, что значения в диапазоне 0-100
        assert 0 <= profile.openness <= 100
        assert 0 <= profile.conscientiousness <= 100
        assert 0 <= profile.extraversion <= 100
        assert 0 <= profile.agreeableness <= 100
        assert 0 <= profile.neuroticism <= 100
    
    def test_reversed_questions(self):
        """Проверка обратного кодирования вопросов"""
        test = BigFiveTest()
        
        # Находим обратный вопрос
        reversed_questions = [q for q in BIG_FIVE_QUESTIONS if q.reversed]
        assert len(reversed_questions) > 0
        
        # Проверяем инверсию
        reversed_q = reversed_questions[0]
        assert reversed_q.calculate_score(AnswerScale.STRONGLY_AGREE) == 1
        assert reversed_q.calculate_score(AnswerScale.STRONGLY_DISAGREE) == 5


class TestBigFiveProfile:
    """Тесты для профиля Big Five"""
    
    def test_to_dict(self):
        """Проверка конвертации в словарь"""
        profile = BigFiveProfile(
            openness=80.0,
            conscientiousness=70.0,
            extraversion=60.0,
            agreeableness=90.0,
            neuroticism=30.0
        )
        
        d = profile.to_dict()
        assert d["openness"] == 80.0
        assert d["conscientiousness"] == 70.0
        assert d["extraversion"] == 60.0
        assert d["agreeableness"] == 90.0
        assert d["neuroticism"] == 30.0
    
    def test_get_dominant_trait(self):
        """Проверка определения доминирующей черты"""
        profile = BigFiveProfile(
            openness=80.0,
            conscientiousness=70.0,
            extraversion=60.0,
            agreeableness=90.0,
            neuroticism=30.0
        )
        
        dominant = profile.get_dominant_trait()
        assert dominant == TraitType.AGREEABLENESS
    
    def test_compatibility_score_identical(self):
        """Совместимость идентичных профилей"""
        profile1 = BigFiveProfile(
            openness=50.0,
            conscientiousness=50.0,
            extraversion=50.0,
            agreeableness=50.0,
            neuroticism=50.0
        )
        profile2 = BigFiveProfile(
            openness=50.0,
            conscientiousness=50.0,
            extraversion=50.0,
            agreeableness=50.0,
            neuroticism=50.0
        )
        
        score = profile1.compatibility_score(profile2)
        assert 0 <= score <= 100
    
    def test_compatibility_score_opposite(self):
        """Совместимость противоположных профилей"""
        profile1 = BigFiveProfile(
            openness=100.0,
            conscientiousness=100.0,
            extraversion=100.0,
            agreeableness=100.0,
            neuroticism=0.0
        )
        profile2 = BigFiveProfile(
            openness=0.0,
            conscientiousness=0.0,
            extraversion=0.0,
            agreeableness=0.0,
            neuroticism=100.0
        )
        
        score = profile1.compatibility_score(profile2)
        assert 0 <= score <= 100


class TestQuestions:
    """Тесты для вопросов"""
    
    def test_all_traits_covered(self):
        """Проверка, что все 5 черт покрыты"""
        traits = set(q.trait for q in BIG_FIVE_QUESTIONS)
        assert len(traits) == 5
        assert TraitType.OPENNESS in traits
        assert TraitType.CONSCIENTIOUSNESS in traits
        assert TraitType.EXTRAVERSION in traits
        assert TraitType.AGREEABLENESS in traits
        assert TraitType.NEUROTICISM in traits
    
    def test_three_questions_per_trait(self):
        """Проверка, что на каждую черту 3 вопроса"""
        for trait in TraitType:
            count = len([q for q in BIG_FIVE_QUESTIONS if q.trait == trait])
            assert count == 3, f"{trait} имеет {count} вопросов вместо 3"

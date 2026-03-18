"""
Big Five (OCEAN) Personality Assessment Model
Психометрическая модель "Большой пятёрки" для оценки личности
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class TraitType(str, Enum):
    """Пять факторов личности OCEAN"""
    OPENNESS = "openness"           # Открытость опыту
    CONSCIENTIOUSNESS = "conscientiousness"  # Добросовестность
    EXTRAVERSION = "extraversion"   # Экстраверсия
    AGREEABLENESS = "agreeableness" # Доброжелательность
    NEUROTICISM = "neuroticism"     # Нейротизм (эмоциональная стабильность)


class AnswerScale(int, Enum):
    """Шкала ответов от 1 до 5"""
    STRONGLY_DISAGREE = 1
    DISAGREE = 2
    NEUTRAL = 3
    AGREE = 4
    STRONGLY_AGREE = 5


@dataclass
class Question:
    """Вопрос теста Big Five"""
    id: int
    text: str
    trait: TraitType
    reversed: bool = False  # Обратный вопрос (нужно инвертировать оценку)
    
    def calculate_score(self, answer: AnswerScale) -> int:
        """Вычисляет балл с учётом обратного кодирования"""
        if self.reversed:
            return 6 - answer.value  # Инвертируем: 1→5, 2→4, 3→3, 4→2, 5→1
        return answer.value


@dataclass
class BigFiveProfile:
    """Профиль личности по модели Big Five"""
    openness: float = 0.0           # 0-100
    conscientiousness: float = 0.0  # 0-100
    extraversion: float = 0.0       # 0-100
    agreeableness: float = 0.0      # 0-100
    neuroticism: float = 0.0        # 0-100
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism
        }
    
    def get_dominant_trait(self) -> TraitType:
        """Возвращает доминирующую черту личности"""
        traits = self.to_dict()
        return TraitType(max(traits, key=traits.get))
    
    def compatibility_score(self, other: 'BigFiveProfile') -> float:
        """
        Рассчитывает совместимость двух профилей (0-100)
        
        Логика совместимости:
        - Открытость: похожие = лучше
        - Добросовестность: похожие = лучше
        - Экстраверсия: комбинация экстраверта и интроверта может работать
        - Доброжелательность: высокая у обоих = лучше
        - Нейротизм: низкий у обоих = лучше
        """
        scores = []
        
        # Открытость - похожие значения лучше
        scores.append(100 - abs(self.openness - other.openness))
        
        # Добросовестность - похожие значения лучше
        scores.append(100 - abs(self.conscientiousness - other.conscientiousness))
        
        # Экстраверсия - умеренная разница может быть хороша
        ext_diff = abs(self.extraversion - other.extraversion)
        scores.append(100 - ext_diff * 0.5)  # Мягче штрафуем разницу
        
        # Доброжелательность - высокие значения лучше
        scores.append((self.agreeableness + other.agreeableness) / 2)
        
        # Нейротизм - низкие значения лучше (эмоциональная стабильность)
        scores.append((200 - self.neuroticism - other.neuroticism) / 2)
        
        return sum(scores) / len(scores)


# Big Five Test - 15 вопросов (3 на каждую черту)
BIG_FIVE_QUESTIONS: List[Question] = [
    # === OPENNESS (Открытость опыту) ===
    Question(
        id=1,
        text="Мне нравится пробовать новые вещи и идеи",
        trait=TraitType.OPENNESS,
        reversed=False
    ),
    Question(
        id=2,
        text="У меня богатое воображение и творческое мышление",
        trait=TraitType.OPENNESS,
        reversed=False
    ),
    Question(
        id=3,
        text="Я предпочитаю привычный порядок вещей, а не перемены",
        trait=TraitType.OPENNESS,
        reversed=True
    ),
    
    # === CONSCIENTIOUSNESS (Добросовестность) ===
    Question(
        id=4,
        text="Я всегда выполняю задачи до конца и не откладываю на потом",
        trait=TraitType.CONSCIENTIOUSNESS,
        reversed=False
    ),
    Question(
        id=5,
        text="Я организованный и пунктуальный человек",
        trait=TraitType.CONSCIENTIOUSNESS,
        reversed=False
    ),
    Question(
        id=6,
        text="Мне сложно придерживаться расписания и планов",
        trait=TraitType.CONSCIENTIOUSNESS,
        reversed=True
    ),
    
    # === EXTRAVERSION (Экстраверсия) ===
    Question(
        id=7,
        text="Я чувствую себя энергичным в больших компаниях",
        trait=TraitType.EXTRAVERSION,
        reversed=False
    ),
    Question(
        id=8,
        text="Я легко завожу новые знакомства и общаюсь с незнакомцами",
        trait=TraitType.EXTRAVERSION,
        reversed=False
    ),
    Question(
        id=9,
        text="Я предпочитаю проводить время один, а не в компании",
        trait=TraitType.EXTRAVERSION,
        reversed=True
    ),
    
    # === AGREEABLENESS (Доброжелательность) ===
    Question(
        id=10,
        text="Я заботлюсь о чувствах других людей",
        trait=TraitType.AGREEABLENESS,
        reversed=False
    ),
    Question(
        id=11,
        text="Я готов помочь другим, даже если это неудобно мне",
        trait=TraitType.AGREEABLENESS,
        reversed=False
    ),
    Question(
        id=12,
        text="Мне сложно находить общий язык с людьми",
        trait=TraitType.AGREEABLENESS,
        reversed=True
    ),
    
    # === NEUROTICISM (Нейротизм / Эмоциональная стабильность) ===
    Question(
        id=13,
        text="Я часто переживаю и волнуюсь по пустякам",
        trait=TraitType.NEUROTICISM,
        reversed=False
    ),
    Question(
        id=14,
        text="Мое настроение часто меняется без причины",
        trait=TraitType.NEUROTICISM,
        reversed=False
    ),
    Question(
        id=15,
        text="Я остаюсь спокойным даже в стрессовых ситуациях",
        trait=TraitType.NEUROTICISM,
        reversed=True
    ),
]


class BigFiveTest:
    """Класс для проведения теста Big Five"""
    
    def __init__(self):
        self.questions = BIG_FIVE_QUESTIONS
    
    def get_questions(self) -> List[Dict]:
        """Возвращает список вопросов для фронтенда"""
        return [
            {
                "id": q.id,
                "text": q.text,
                "trait": q.trait.value
            }
            for q in self.questions
        ]
    
    def calculate_profile(self, answers: Dict[int, int]) -> BigFiveProfile:
        """
        Рассчитывает профиль Big Five на основе ответов
        
        Args:
            answers: Словарь {question_id: answer_value (1-5)}
        
        Returns:
            BigFiveProfile с нормализованными значениями (0-100)
        """
        trait_scores = {trait: [] for trait in TraitType}
        
        for question in self.questions:
            if question.id in answers:
                answer = AnswerScale(answers[question.id])
                score = question.calculate_score(answer)
                trait_scores[question.trait].append(score)
        
        # Усредняем и нормализуем в 0-100
        return BigFiveProfile(
            openness=self._normalize(sum(trait_scores[TraitType.OPENNESS]) / 3),
            conscientiousness=self._normalize(sum(trait_scores[TraitType.CONSCIENTIOUSNESS]) / 3),
            extraversion=self._normalize(sum(trait_scores[TraitType.EXTRAVERSION]) / 3),
            agreeableness=self._normalize(sum(trait_scores[TraitType.AGREEABLENESS]) / 3),
            neuroticism=self._normalize(sum(trait_scores[TraitType.NEUROTICISM]) / 3)
        )
    
    @staticmethod
    def _normalize(score: float) -> float:
        """Нормализует балл 1-5 в 0-100"""
        return round((score - 1) / 4 * 100, 1)


# Pydantic модели для API
class AnswerRequest(BaseModel):
    """Модель ответа на вопрос"""
    question_id: int = Field(..., ge=1, le=15)
    value: int = Field(..., ge=1, le=5)


class TestSubmission(BaseModel):
    """Модель отправки результатов теста"""
    answers: List[AnswerRequest]


class BigFiveResponse(BaseModel):
    """Модель ответа с профилем Big Five"""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    dominant_trait: str
    interpretation: Dict[str, str]


class QuestionResponse(BaseModel):
    """Модель вопроса для API"""
    id: int
    text: str
    trait: str

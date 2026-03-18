"""
MBTI Personality Types
Типология личности Майерс-Бриггс

16 типов личности на основе 4 дихотомий:
- E/I: Экстраверсия / Интроверсия
- S/N: Сенсорика / Интуиция
- T/F: Мышление / Чувство
- J/P: Суждение / Восприятие
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class MBTIDimension(str, Enum):
    """Дихотомии MBTI"""
    EXTRAVERSION = "E"
    INTROVERSION = "I"
    SENSING = "S"
    INTUITION = "N"
    THINKING = "T"
    FEELING = "F"
    JUDGING = "J"
    PERCEIVING = "P"


@dataclass
class MBTIType:
    """Тип MBTI"""
    code: str
    name: str
    description: str
    strengths: list
    weaknesses: list
    careers: list
    compatible_with: list


# Описания всех 16 типов MBTI
MBTI_TYPES: Dict[str, MBTIType] = {
    "INTJ": MBTIType(
        code="INTJ",
        name="Архитектор",
        description="Стратегический мыслитель, любит планировать и ставить цели.",
        strengths=["Стратегическое мышление", "Независимость", "Целеустремленность"],
        weaknesses=["Перфекционизм", "Сложности в общении", "Критичность"],
        careers=["Аналитик", "Программист", "Ученый", "Руководитель"],
        compatible_with=["ENFP", "ENTP"]
    ),
    "INTP": MBTIType(
        code="INTP",
        name="Логик",
        description="Творческий изобретатель, любит теории и абстракции.",
        strengths=["Аналитический ум", "Креативность", "Объективность"],
        weaknesses=["Прокрастинация", "Социальная неуклюжесть", "Нерешительность"],
        careers=["Программист", "Физик", "Философ", "Исследователь"],
        compatible_with=["ENTJ", "ESTJ"]
    ),
    "ENTJ": MBTIType(
        code="ENTJ",
        name="Командир",
        description="Прирожденный лидер, любит организовывать и управлять.",
        strengths=["Лидерство", "Эффективность", "Уверенность"],
        weaknesses=["Нетерпимость", "Агрессивность", "Работоголизм"],
        careers=["CEO", "Предприниматель", "Юрист", "Консультант"],
        compatible_with=["INFP", "INTP"]
    ),
    "ENTP": MBTIType(
        code="ENTP",
        name="Полемист",
        description="Инноватор, любит дебаты и новые идеи.",
        strengths=["Креативность", "Коммуникабельность", "Адаптивность"],
        weaknesses=["Непостоянство", "Аргументативность", "Нетерпение"],
        careers=["Предприниматель", "Юрист", "Журналист", "Консультант"],
        compatible_with=["INFJ", "INTJ"]
    ),
    "INFJ": MBTIType(
        code="INFJ",
        name="Адвокат",
        description="Тихий идеалист, стремится к гармонии и смыслу.",
        strengths=["Эмпатия", "Интуиция", "Целеустремленность"],
        weaknesses=["Чувствительность", "Замкнутость", "Выгорание"],
        careers=["Психолог", "Писатель", "Консультант", "Учитель"],
        compatible_with=["ENFP", "ENTP"]
    ),
    "INFP": MBTIType(
        code="INFP",
        name="Посредник",
        description="Мечтатель, ценит аутентичность и творчество.",
        strengths=["Креативность", "Эмпатия", "Идеализм"],
        weaknesses=["Чувствительность", "Нерешительность", "Изоляция"],
        careers=["Писатель", "Художник", "Психолог", "Музыкант"],
        compatible_with=["ENFJ", "ESFJ"]
    ),
    "ENFJ": MBTIType(
        code="ENFJ",
        name="Протагонист",
        description="Харизматичный лидер, вдохновляет других.",
        strengths=["Харизма", "Эмпатия", "Лидерство"],
        weaknesses=["Зависимость от мнения", "Выгорание", "Идеализация"],
        careers=["Учитель", "HR", "Консультант", "Политик"],
        compatible_with=["INFP", "ISFP"]
    ),
    "ENFP": MBTIType(
        code="ENFP",
        name="Борец",
        description="Энтузиаст, полный энергии и идей.",
        strengths=["Креативность", "Коммуникабельность", "Энтузиазм"],
        weaknesses=[["Нефокусированность", "Эмоциональность", "Прокрастинация"]],
        careers=["Журналист", "Актер", "Предприниматель", "Консультант"],
        compatible_with=["INFJ", "INTJ"]
    ),
    "ISTJ": MBTIType(
        code="ISTJ",
        name="Логистик",
        description="Надежный и организованный, ценит традиции.",
        strengths=["Надежность", "Организованность", "Практичность"],
        weaknesses=["Консервативность", "Жесткость", "Эмоциональная сдержанность"],
        careers=["Бухгалтер", "Юрист", "Военный", "Администратор"],
        compatible_with=["ESFP", "ESTP"]
    ),
    "ISFJ": MBTIType(
        code="ISFJ",
        name="Защитник",
        description="Заботливый и преданный, помогает другим.",
        strengths=["Заботливость", "Надежность", "Терпение"],
        weaknesses=[["Самопожертвование", "Конфликтофобия", "Скромность"]],
        careers=["Медсестра", "Социальный работник", "Бухгалтер", "Администратор"],
        compatible_with=["ESFP", "ESTP"]
    ),
    "ESTJ": MBTIType(
        code="ESTJ",
        name="Исполнитель",
        description="Практичный организатор, ценит порядок.",
        strengths=["Организованность", "Практичность", "Лидерство"],
        weaknesses=["Негибкость", "Критичность", "Нетерпимость"],
        careers=["Менеджер", "Администратор", "Военный", "Судья"],
        compatible_with=["ISFP", "ISTP"]
    ),
    "ESFJ": MBTIType(
        code="ESFJ",
        name="Консул",
        description="Общительный и заботливый, ценит гармонию.",
        strengths=[["Коммуникабельность", "Заботливость", "Организованность"]],
        weaknesses=["Зависимость от мнения", "Конфликтофобия", "Самопожертвование"],
        careers=["Учитель", "HR", "Медсестра", "Социальный работник"],
        compatible_with=["ISFP", "ISTP"]
    ),
    "ISTP": MBTIType(
        code="ISTP",
        name="Виртуоз",
        description="Практичный экспериментатор, любит технику.",
        strengths=["Практичность", "Аналитичность", "Независимость"],
        weaknesses=["Сдержанность", "Рискованность", "Нетерпение"],
        careers=["Инженер", "Пилот", "Программист", "Детектив"],
        compatible_with=["ESFJ", "ESTJ"]
    ),
    "ISFP": MBTIType(
        code="ISFP",
        name="Артист",
        description="Творческий и чувствительный, ценит красоту.",
        strengths=["Креативность", "Чувствительность", "Гибкость"],
        weaknesses=["Конфликтофобия", "Нерешительность", "Изоляция"],
        careers=["Художник", "Музыкант", "Дизайнер", "Фотограф"],
        compatible_with=["ENFJ", "ESFJ"]
    ),
    "ESTP": MBTIType(
        code="ESTP",
        name="Делец",
        description="Энергичный прагматик, живет здесь и сейчас.",
        strengths=["Энергичность", "Практичность", "Харизма"],
        weaknesses=["Импульсивность", "Нетерпение", "Рискованность"],
        careers=["Предприниматель", "Продавец", "Спортсмен", "Детектив"],
        compatible_with=["ISFJ", "ISTJ"]
    ),
    "ESFP": MBTIType(
        code="ESFP",
        name="Развлекатель",
        description="Общительный и энергичный, любит веселье.",
        strengths=["Коммуникабельность", "Энергичность", "Гибкость"],
        weaknesses=["Нефокусированность", "Импульсивность", "Чувствительность"],
        careers=["Актер", "Ведущий", "PR", "Продавец"],
        compatible_with=["ISFJ", "ISTJ"]
    )
}


class MBTIAnalyzer:
    """Анализатор типов MBTI"""
    
    def __init__(self):
        self.types = MBTI_TYPES
    
    def get_type(self, code: str) -> Optional[MBTIType]:
        """Получить описание типа по коду"""
        return self.types.get(code.upper())
    
    def get_all_types(self) -> Dict[str, MBTIType]:
        """Получить все типы"""
        return self.types
    
    def analyze_compatibility(self, type1: str, type2: str) -> Dict[str, Any]:
        """Анализ совместимости двух типов"""
        t1 = self.get_type(type1)
        t2 = self.get_type(type2)
        
        if not t1 or not t2:
            return {"error": "Invalid type code"}
        
        # Проверяем прямую совместимость
        direct_compatible = type2 in t1.compatible_with
        
        # Анализируем функции
        functions1 = self._get_cognitive_functions(type1)
        functions2 = self._get_cognitive_functions(type2)
        
        # Считаем совпадения функций
        matching_functions = set(functions1) & set(functions2)
        
        # Оценка совместимости
        score = 0
        if direct_compatible:
            score += 40
        score += len(matching_functions) * 10
        
        # Дополнительные баллы за дополнительность
        if type1[0] != type2[0]:  # E/I
            score += 10
        if type1[2] != type2[2]:  # T/F
            score += 10
        
        return {
            "type1": type1,
            "type2": type2,
            "score": min(score, 100),
            "direct_compatible": direct_compatible,
            "matching_functions": list(matching_functions),
            "recommendation": self._get_compatibility_recommendation(score)
        }
    
    def _get_cognitive_functions(self, mbti_type: str) -> list:
        """Получить когнитивные функции типа"""
        functions_map = {
            "INTJ": ["Ni", "Te", "Fi", "Se"],
            "INTP": ["Ti", "Ne", "Si", "Fe"],
            "ENTJ": ["Te", "Ni", "Se", "Fi"],
            "ENTP": ["Ne", "Ti", "Fe", "Si"],
            "INFJ": ["Ni", "Fe", "Ti", "Se"],
            "INFP": ["Fi", "Ne", "Si", "Te"],
            "ENFJ": ["Fe", "Ni", "Se", "Ti"],
            "ENFP": ["Ne", "Fi", "Te", "Si"],
            "ISTJ": ["Si", "Te", "Fi", "Ne"],
            "ISFJ": ["Si", "Fe", "Ti", "Ne"],
            "ESTJ": ["Te", "Si", "Ne", "Fi"],
            "ESFJ": ["Fe", "Si", "Ne", "Ti"],
            "ISTP": ["Ti", "Se", "Ni", "Fe"],
            "ISFP": ["Fi", "Se", "Ni", "Te"],
            "ESTP": ["Se", "Ti", "Fe", "Ni"],
            "ESFP": ["Se", "Fi", "Te", "Ni"]
        }
        return functions_map.get(mbti_type, [])
    
    def _get_compatibility_recommendation(self, score: int) -> str:
        """Получить рекомендацию по совместимости"""
        if score >= 80:
            return "Отличная совместимость! Вы дополняете друг друга."
        elif score >= 60:
            return "Хорошая совместимость. Есть потенциал для роста."
        elif score >= 40:
            return "Средняя совместимость. Потребуется работа над отношениями."
        else:
            return "Сложная совместимость. Будьте терпеливы и открыты."
    
    def format_type_description(self, mbti_type: str) -> str:
        """Форматировать описание типа для отображения"""
        t = self.get_type(mbti_type)
        if not t:
            return f"Тип {mbti_type} не найден"
        
        return f"""
🎯 {t.code} — {t.name}
━━━━━━━━━━━━━━━━━━━━━━━━
{t.description}

💪 Сильные стороны:
{chr(10).join(f"  • {s}" for s in t.strengths)}

⚠️ Слабые стороны:
{chr(10).join(f"  • {w}" for w in t.weaknesses)}

💼 Подходящие профессии:
{', '.join(t.careers)}

❤️ Совместимость: {', '.join(t.compatible_with)}
"""


# Singleton
_mbti_analyzer: Optional[MBTIAnalyzer] = None


def get_mbti_analyzer() -> MBTIAnalyzer:
    """Получить анализатор MBTI"""
    global _mbti_analyzer
    if _mbti_analyzer is None:
        _mbti_analyzer = MBTIAnalyzer()
    return _mbti_analyzer

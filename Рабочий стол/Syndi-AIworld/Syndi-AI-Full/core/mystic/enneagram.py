"""
Enneagram Personality Types
Эннеаграмма — 9 типов личности

Каждый тип имеет:
- Базовый страх
- Базовое желание
- Крылья (соседние типы)
- Уровни развития
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class EnneagramType(Enum):
    """9 типов эннеаграммы"""
    REFORMER = 1
    HELPER = 2
    ACHIEVER = 3
    INDIVIDUALIST = 4
    INVESTIGATOR = 5
    LOYALIST = 6
    ENTHUSIAST = 7
    CHALLENGER = 8
    PEACEMAKER = 9


@dataclass
class EnneagramDescription:
    """Описание типа эннеаграммы"""
    number: int
    name: str
    nickname: str
    basic_fear: str
    basic_desire: str
    key_motivations: List[str]
    strengths: List[str]
    challenges: List[str]
    wings: List[int]
    integration: int  # Тип в здоровом состоянии
    disintegration: int  # Тип в стрессе


# Описания всех 9 типов
ENNEAGRAM_TYPES: Dict[int, EnneagramDescription] = {
    1: EnneagramDescription(
        number=1,
        name="Реформатор",
        nickname="Идеалист",
        basic_fear="Быть плохим, неправильным, безнравственным",
        basic_desire="Быть правильным, хорошим, совершенным",
        key_motivations=[
            "Стремление к совершенству",
            "Улучшение мира",
            "Справедливость"
        ],
        strengths=[
            "Честность и целостность",
            "Ответственность",
            "Внимание к деталям",
            "Организованность"
        ],
        challenges=[
            "Критичность к себе и другим",
            "Перфекционизм",
            "Жесткость",
            "Подавление гнева"
        ],
        wings=[9, 2],
        integration=7,
        disintegration=4
    ),
    2: EnneagramDescription(
        number=2,
        name="Помощник",
        nickname="Заботливый",
        basic_fear="Быть нежеланным, ненужным",
        basic_desire="Быть любимым, нужным",
        key_motivations=[
            "Помощь другим",
            "Признание",
            "Близость в отношениях"
        ],
        strengths=[
            "Эмпатия и забота",
            "Щедрость",
            "Коммуникабельность",
            "Поддержка других"
        ],
        challenges=[
            "Забывание своих нужд",
            "Манипуляция через заботу",
            "Зависимость от признания",
            "Гнев от неблагодарности"
        ],
        wings=[1, 3],
        integration=4,
        disintegration=8
    ),
    3: EnneagramDescription(
        number=3,
        name="Достигатор",
        nickname="Успешный",
        basic_fear="Быть неудачником, бесполезным",
        basic_desire="Быть успешным, ценным",
        key_motivations=[
            "Достижение целей",
            "Признание",
            "Эффективность"
        ],
        strengths=[
            "Целеустремленность",
            "Адаптивность",
            "Харизма",
            "Практичность"
        ],
        challenges=[
            "Работоголизм",
            "Потеря себя в ролях",
            "Зависть",
            "Поверхностность"
        ],
        wings=[2, 4],
        integration=6,
        disintegration=9
    ),
    4: EnneagramDescription(
        number=4,
        name="Индивидуалист",
        nickname="Романтик",
        basic_fear="Не иметь значения, быть обычным",
        basic_desire="Быть уникальным, значимым",
        key_motivations=[
            "Самовыражение",
            "Поиск смысла",
            "Аутентичность"
        ],
        strengths=[
            "Креативность",
            "Эмоциональная глубина",
            "Аутентичность",
            "Эмпатия"
        ],
        challenges=[
            "Меланхолия",
            "Зависть",
            "Драматизация",
            "Изоляция"
        ],
        wings=[3, 5],
        integration=1,
        disintegration=2
    ),
    5: EnneagramDescription(
        number=5,
        name="Исследователь",
        nickname="Наблюдатель",
        basic_fear="Быть беспомощным, неспособным",
        basic_desire="Быть компетентным, знающим",
        key_motivations=[
            "Познание",
            "Независимость",
            "Приватность"
        ],
        strengths=[
            "Аналитический ум",
            "Независимость",
            "Концентрация",
            "Объективность"
        ],
        challenges=[
            "Изоляция",
            "Скупость",
            "Арогантность",
            "Отстраненность"
        ],
        wings=[4, 6],
        integration=8,
        disintegration=7
    ),
    6: EnneagramDescription(
        number=6,
        name="Лоялист",
        nickname="Верный",
        basic_fear="Быть без поддержки, незащищенным",
        basic_desire="Быть в безопасности, иметь поддержку",
        key_motivations=[
            "Безопасность",
            "Верность",
            "Ответственность"
        ],
        strengths=[
            "Надежность",
            "Преданность",
            "Анализ рисков",
            "Честность"
        ],
        challenges=[
            "Тревожность",
            "Сомнения",
            "Зависимость",
            "Пессимизм"
        ],
        wings=[5, 7],
        integration=9,
        disintegration=3
    ),
    7: EnneagramDescription(
        number=7,
        name="Энтузиаст",
        nickname="Оптимист",
        basic_fear="Быть в ловушке боли, лишенным",
        basic_desire="Быть счастливым, удовлетворенным",
        key_motivations=[
            "Новый опыт",
            "Свобода",
            "Удовольствие"
        ],
        strengths=[
            "Оптимизм",
            "Креативность",
            "Адаптивность",
            "Энтузиазм"
        ],
        challenges=[
            "Избегание проблем",
            "Непостоянство",
            "Импульсивность",
            "Поверхностность"
        ],
        wings=[6, 8],
        integration=5,
        disintegration=1
    ),
    8: EnneagramDescription(
        number=8,
        name="Борец",
        nickname="Лидер",
        basic_fear="Быть контролируемым, слабым",
        basic_desire="Защищать себя, контролировать",
        key_motivations=[
            "Контроль",
            "Справедливость",
            "Сила"
        ],
        strengths=[
            "Лидерство",
            "Решительность",
            "Защита слабых",
            "Прямота"
        ],
        challenges=[
            "Агрессивность",
            "Контроль",
            "Нетерпимость",
            "Уязвимость"
        ],
        wings=[7, 9],
        integration=2,
        disintegration=5
    ),
    9: EnneagramDescription(
        number=9,
        name="Миротворец",
        nickname="Посредник",
        basic_fear="Разъединение, конфликт",
        basic_desire="Внутренний покой, гармония",
        key_motivations=[
            "Мир",
            "Стабильность",
            "Единство"
        ],
        strengths=[
            "Терпимость",
            "Спокойствие",
            "Эмпатия",
            "Примирение"
        ],
        challenges=[
            "Пассивность",
            "Упрямство",
            "Забывание себя",
            "Резистентность"
        ],
        wings=[8, 1],
        integration=3,
        disintegration=6
    )
}


class EnneagramAnalyzer:
    """Анализатор эннеаграммы"""
    
    def __init__(self):
        self.types = ENNEAGRAM_TYPES
    
    def get_type(self, number: int) -> Optional[EnneagramDescription]:
        """Получить описание типа по номеру"""
        return self.types.get(number)
    
    def get_type_by_code(self, code: str) -> Optional[EnneagramDescription]:
        """Получить тип по коду (например, '4w5')"""
        # Парсим код типа с крылом
        if 'w' in code:
            main_type = int(code.split('w')[0])
            wing = int(code.split('w')[1])
            return self.types.get(main_type)
        else:
            return self.types.get(int(code))
    
    def get_wing_description(self, main_type: int, wing: int) -> str:
        """Получить описание крыла"""
        main = self.get_type(main_type)
        wing_type = self.get_type(wing)
        
        if not main or not wing_type:
            return "Неизвестный тип"
        
        return f"{main.name} с крылом {wing_type.name}: {main.nickname} + {wing_type.nickname}"
    
    def analyze_stress_growth(self, type_number: int) -> Dict[str, Any]:
        """Анализ типа в стрессе и росте"""
        t = self.get_type(type_number)
        if not t:
            return {"error": "Invalid type"}
        
        integration = self.get_type(t.integration)
        disintegration = self.get_type(t.disintegration)
        
        return {
            "type": t.name,
            "in_stress": {
                "goes_to": disintegration.name if disintegration else "Unknown",
                "behavior": self._get_stress_behavior(type_number)
            },
            "in_growth": {
                "goes_to": integration.name if integration else "Unknown",
                "behavior": self._get_growth_behavior(type_number)
            }
        }
    
    def _get_stress_behavior(self, type_number: int) -> str:
        """Поведение типа в стрессе"""
        behaviors = {
            1: "Становится раздражительным и критичным",
            2: "Становится агрессивным и контролирующим",
            3: "Становится пассивным и отстраненным",
            4: "Становится навязчивым и жертвенным",
            5: "Становится импульсивным и рассеянным",
            6: "Становится конкурентным и амбициозным",
            7: "Становится критичным и перфекционистским",
            8: "Становится скрытным и аналитическим",
            9: "Становится тревожным и сомневающимся"
        }
        return behaviors.get(type_number, "Неизвестное поведение")
    
    def _get_growth_behavior(self, type_number: int) -> str:
        """Поведение типа в росте"""
        behaviors = {
            1: "Становится спонтанным и радостным",
            2: "Становится аутентичным и творческим",
            3: "Становится верным и ответственным",
            4: "Становится целеустремленным и организованным",
            5: "Становится решительным и лидерским",
            6: "Становится спокойным и гармоничным",
            7: "Становится сфокусированным и глубоким",
            8: "Становится заботливым и открытым",
            9: "Становится амбициозным и эффективным"
        }
        return behaviors.get(type_number, "Неизвестное поведение")
    
    def format_type_description(self, type_number: int, wing: Optional[int] = None) -> str:
        """Форматировать описание типа для отображения"""
        t = self.get_type(type_number)
        if not t:
            return f"Тип {type_number} не найден"
        
        wing_text = ""
        if wing and wing in t.wings:
            wing_type = self.get_type(wing)
            if wing_type:
                wing_text = f" ({t.number}w{wing} — с крылом {wing_type.name})"
        
        return f"""
🔮 Эннеаграмма {t.number} — {t.name}{wing_text}
━━━━━━━━━━━━━━━━━━━━━━━━
{t.nickname}

😨 Базовый страх:
{t.basic_fear}

✨ Базовое желание:
{t.basic_desire}

💪 Сильные стороны:
{chr(10).join(f"  • {s}" for s in t.strengths)}

⚠️ Сложности:
{chr(10).join(f"  • {c}" for c in t.challenges)}

🔄 Интеграция → Тип {t.integration} (в росте)
💔 Дезинтеграция → Тип {t.disintegration} (в стрессе)
"""


# Singleton
_enneagram_analyzer: Optional[EnneagramAnalyzer] = None


def get_enneagram_analyzer() -> EnneagramAnalyzer:
    """Получить анализатор эннеаграммы"""
    global _enneagram_analyzer
    if _enneagram_analyzer is None:
        _enneagram_analyzer = EnneagramAnalyzer()
    return _enneagram_analyzer

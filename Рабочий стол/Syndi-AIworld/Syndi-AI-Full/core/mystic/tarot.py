"""
Tarot Card System
Система карт Таро

78 карт:
- 22 Старших Аркана
- 56 Младших Аркана (4 масти по 14 карт)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import random


class TarotSuit(Enum):
    """Масти Таро"""
    WANDS = "Жезлы"      # Огонь, творчество, действие
    CUPS = "Кубки"       # Вода, эмоции, отношения
    SWORDS = "Мечи"      # Воздух, мысли, конфликты
    PENTACLES = "Пентакли"  # Земля, материя, деньги


@dataclass
class TarotCard:
    """Карта Таро"""
    id: int
    name: str
    arcana: str  # "major" или "minor"
    suit: Optional[TarotSuit]
    number: Optional[int]  # Для младших арканов
    keywords: List[str]
    meaning_upright: str
    meaning_reversed: str
    element: str
    planet: Optional[str]
    zodiac: Optional[str]


# Старшие Арканы (22 карты)
MAJOR_ARCANA: Dict[int, TarotCard] = {
    0: TarotCard(
        id=0,
        name="Шут",
        arcana="major",
        suit=None,
        number=0,
        keywords=["Начало", "Невинность", "Спонтанность"],
        meaning_upright="Новое начало, чистый лист, приключение, потенциал",
        meaning_reversed="Безрассудство, наивность, упущенная возможность",
        element="Воздух",
        planet="Уран",
        zodiac=None
    ),
    1: TarotCard(
        id=1,
        name="Маг",
        arcana="major",
        suit=None,
        number=1,
        keywords=["Сила воли", "Мастерство", "Ресурсы"],
        meaning_upright="Сила воли, мастерство, ресурсы, проявление",
        meaning_reversed="Манипуляция, обман, неиспользованный потенциал",
        element="Воздух",
        planet="Меркурий",
        zodiac=None
    ),
    2: TarotCard(
        id=2,
        name="Верховная Жрица",
        arcana="major",
        suit=None,
        number=2,
        keywords=["Интуиция", "Подсознание", "Тайны"],
        meaning_upright="Интуиция, подсознание, тайные знания, внутренний голос",
        meaning_reversed="Секреты, отстраненность, игнорирование интуиции",
        element="Вода",
        planet="Луна",
        zodiac=None
    ),
    3: TarotCard(
        id=3,
        name="Императрица",
        arcana="major",
        suit=None,
        number=3,
        keywords=["Изобилие", "Материнство", "Творчество"],
        meaning_upright="Изобилие, плодородие, творчество, забота",
        meaning_reversed="Зависимость, пустота, творческий кризис",
        element="Земля",
        planet="Венера",
        zodiac=None
    ),
    4: TarotCard(
        id=4,
        name="Император",
        arcana="major",
        suit=None,
        number=4,
        keywords=["Власть", "Структура", "Контроль"],
        meaning_upright="Власть, структура, контроль, отцовство, стабильность",
        meaning_reversed="Тирания, жесткость, потеря контроля",
        element="Огонь",
        planet="Марс",
        zodiac="Овен"
    ),
    5: TarotCard(
        id=5,
        name="Иерофант",
        arcana="major",
        suit=None,
        number=5,
        keywords=["Традиции", "Духовность", "Учение"],
        meaning_upright="Традиции, духовность, обучение, конформизм",
        meaning_reversed="Бунт, нетрадиционность, догматизм",
        element="Земля",
        planet="Юпитер",
        zodiac="Телец"
    ),
    6: TarotCard(
        id=6,
        name="Влюбленные",
        arcana="major",
        suit=None,
        number=6,
        keywords=["Любовь", "Гармония", "Выбор"],
        meaning_upright="Любовь, гармония, отношения, выбор, союз",
        meaning_reversed="Разрыв, несоответствие, дилемма",
        element="Воздух",
        planet="Меркурий",
        zodiac="Близнецы"
    ),
    7: TarotCard(
        id=7,
        name="Колесница",
        arcana="major",
        suit=None,
        number=7,
        keywords=["Движение", "Контроль", "Победа"],
        meaning_upright="Движение вперед, контроль, победа, решительность",
        meaning_reversed="Потеря контроля, поражение, агрессия",
        element="Вода",
        planet=None,
        zodiac="Рак"
    ),
    8: TarotCard(
        id=8,
        name="Сила",
        arcana="major",
        suit=None,
        number=8,
        keywords=["Сила", "Мужество", "Убеждение"],
        meaning_upright="Внутренняя сила, мужество, убеждение, сострадание",
        meaning_reversed="Слабость, сомнения, подавление",
        element="Огонь",
        planet="Солнце",
        zodiac="Лев"
    ),
    9: TarotCard(
        id=9,
        name="Отшельник",
        arcana="major",
        suit=None,
        number=9,
        keywords=["Одиночество", "Поиск", "Внутренний свет"],
        meaning_upright="Одиночество, поиск истины, внутренняя мудрость",
        meaning_reversed="Изоляция, потеря пути, одиночество",
        element="Земля",
        planet="Меркурий",
        zodiac="Дева"
    ),
    10: TarotCard(
        id=10,
        name="Колесо Фортуны",
        arcana="major",
        suit=None,
        number=10,
        keywords=["Судьба", "Циклы", "Удача"],
        meaning_upright="Судьба, циклы, удача, перемены, карма",
        meaning_reversed="Невезение, сопротивление переменам, застой",
        element="Огонь",
        planet="Юпитер",
        zodiac=None
    ),
    11: TarotCard(
        id=11,
        name="Справедливость",
        arcana="major",
        suit=None,
        number=11,
        keywords=["Справедливость", "Баланс", "Закон"],
        meaning_upright="Справедливость, баланс, закон, честность",
        meaning_reversed="Несправедливость, нечестность, несбалансированность",
        element="Воздух",
        planet=None,
        zodiac="Весы"
    ),
    12: TarotCard(
        id=12,
        name="Повешенный",
        arcana="major",
        suit=None,
        number=12,
        keywords=["Жертва", "Пауза", "Новый взгляд"],
        meaning_upright="Жертва, пауза, новый взгляд, отпускание",
        meaning_reversed="Сопротивление, застой, бесполезная жертва",
        element="Вода",
        planet="Нептун",
        zodiac=None
    ),
    13: TarotCard(
        id=13,
        name="Смерть",
        arcana="major",
        suit=None,
        number=13,
        keywords=["Трансформация", "Конец", "Начало"],
        meaning_upright="Трансформация, конец старого, новое начало",
        meaning_reversed="Сопротивление переменам, застой, страх смерти",
        element="Вода",
        planet="Плутон",
        zodiac="Скорпион"
    ),
    14: TarotCard(
        id=14,
        name="Умеренность",
        arcana="major",
        suit=None,
        number=14,
        keywords=["Баланс", "Умеренность", "Смешение"],
        meaning_upright="Баланс, умеренность, гармония, терпение",
        meaning_reversed="Крайности, несбалансированность, избыток",
        element="Огонь",
        planet="Юпитер",
        zodiac="Стрелец"
    ),
    15: TarotCard(
        id=15,
        name="Дьявол",
        arcana="major",
        suit=None,
        number=15,
        keywords=["Искушение", "Зависимость", "Материализм"],
        meaning_upright="Искушение, зависимость, материализм, иллюзии",
        meaning_reversed="Освобождение, преодоление зависимости, прозрение",
        element="Земля",
        planet="Сатурн",
        zodiac="Козерог"
    ),
    16: TarotCard(
        id=16,
        name="Башня",
        arcana="major",
        suit=None,
        number=16,
        keywords=[["Разрушение", "Кризис", "Пробуждение"]],
        meaning_upright="Внезапные перемены, разрушение, кризис, пробуждение",
        meaning_reversed="Избегание перемен, отсрочка неизбежного",
        element="Огонь",
        planet="Марс",
        zodiac=None
    ),
    17: TarotCard(
        id=17,
        name="Звезда",
        arcana="major",
        suit=None,
        number=17,
        keywords=["Надежда", "Вдохновение", "Духовность"],
        meaning_upright="Надежда, вдохновение, духовность, обновление",
        meaning_reversed="Потеря надежды, отчаяние, нереалистичность",
        element="Воздух",
        planet=None,
        zodiac="Водолей"
    ),
    18: TarotCard(
        id=18,
        name="Луна",
        arcana="major",
        suit=None,
        number=18,
        keywords=["Иллюзии", "Страх", "Подсознание"],
        meaning_upright="Иллюзии, страх, подсознание, интуиция",
        meaning_reversed="Прозрение, преодоление страха, ясность",
        element="Вода",
        planet="Луна",
        zodiac="Рыбы"
    ),
    19: TarotCard(
        id=19,
        name="Солнце",
        arcana="major",
        suit=None,
        number=19,
        keywords=["Радость", "Успех", "Позитив"],
        meaning_upright="Радость, успех, позитив, энергия, счастье",
        meaning_reversed="Временная грусть, задержка успеха, пессимизм",
        element="Огонь",
        planet="Солнце",
        zodiac=None
    ),
    20: TarotCard(
        id=20,
        name="Суд",
        arcana="major",
        suit=None,
        number=20,
        keywords=["Возрождение", "Оценка", "Прощение"],
        meaning_upright="Возрождение, оценка, прощение, новый этап",
        meaning_reversed="Самокритика, отказ прощать, застой",
        element="Огонь",
        planet="Плутон",
        zodiac=None
    ),
    21: TarotCard(
        id=21,
        name="Мир",
        arcana="major",
        suit=None,
        number=21,
        keywords=["Завершение", "Целостность", "Достижение"],
        meaning_upright="Завершение, целостность, достижение, интеграция",
        meaning_reversed="Незавершенность, пустота, отсутствие закрытия",
        element="Земля",
        planet="Сатурн",
        zodiac=None
    )
}


class TarotDeck:
    """Колода Таро"""
    
    def __init__(self):
        self.cards = list(MAJOR_ARCANA.values())
        self.shuffled = False
    
    def shuffle(self):
        """Перетасовать колоду"""
        random.shuffle(self.cards)
        self.shuffled = True
    
    def draw(self, num_cards: int = 1) -> List[TarotCard]:
        """Вытянуть карты"""
        if not self.shuffled:
            self.shuffle()
        
        drawn = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return drawn
    
    def reset(self):
        """Сбросить колоду"""
        self.cards = list(MAJOR_ARCANA.values())
        self.shuffled = False
    
    def get_card(self, card_id: int) -> Optional[TarotCard]:
        """Получить карту по ID"""
        return MAJOR_ARCANA.get(card_id)
    
    def get_all_cards(self) -> List[TarotCard]:
        """Получить все карты"""
        return list(MAJOR_ARCANA.values())


class TarotSpread:
    """Расклад Таро"""
    
    SPREADS = {
        "single": {
            "name": "Одна карта",
            "description": "Быстрый ответ на вопрос",
            "positions": ["Суть ситуации"]
        },
        "three_card": {
            "name": "Три карты",
            "description": "Прошлое, настоящее, будущее",
            "positions": ["Прошлое", "Настоящее", "Будущее"]
        },
        "celtic_cross": {
            "name": "Кельтский крест",
            "description": "Подробный расклад на ситуацию",
            "positions": [
                "Суть ситуации",
                "Препятствие",
                "Основа",
                "Прошлое",
                "Лучший исход",
                "Ближайшее будущее",
                "Ваше отношение",
                "Внешнее влияние",
                "Надежды/Страхи",
                "Итог"
            ]
        }
    }
    
    def __init__(self):
        self.deck = TarotDeck()
    
    def do_spread(
        self,
        spread_type: str = "three_card",
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Сделать расклад
        
        Args:
            spread_type: Тип расклада (single, three_card, celtic_cross)
            question: Вопрос для расклада
        
        Returns:
            Результат расклада
        """
        spread_info = self.SPREADS.get(spread_type)
        if not spread_info:
            return {"error": f"Unknown spread type: {spread_type}"}
        
        # Сброс и тасование
        self.deck.reset()
        self.deck.shuffle()
        
        # Вытягиваем карты
        num_cards = len(spread_info["positions"])
        cards = self.deck.draw(num_cards)
        
        # Определяем ориентацию карт (прямая/перевернутая)
        result = {
            "spread_type": spread_type,
            "spread_name": spread_info["name"],
            "question": question,
            "positions": []
        }
        
        for i, (card, position) in enumerate(zip(cards, spread_info["positions"])):
            # Случайная ориентация (70% прямая, 30% перевернутая)
            is_reversed = random.random() < 0.3
            
            result["positions"].append({
                "position": i + 1,
                "position_name": position,
                "card": {
                    "id": card.id,
                    "name": card.name,
                    "keywords": card.keywords,
                    "element": card.element,
                    "planet": card.planet,
                    "zodiac": card.zodiac
                },
                "orientation": "reversed" if is_reversed else "upright",
                "meaning": card.meaning_reversed if is_reversed else card.meaning_upright
            })
        
        return result
    
    def format_spread(self, result: Dict[str, Any]) -> str:
        """Форматировать расклад для отображения"""
        lines = [
            f"🔮 {result['spread_name']}",
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        ]
        
        if result.get('question'):
            lines.append(f"❓ Вопрос: {result['question']}")
            lines.append("")
        
        for pos in result['positions']:
            orientation = "🔄 Перевернутая" if pos['orientation'] == 'reversed' else "⬆️ Прямая"
            lines.append(f"{pos['position']}. {pos['position_name']}")
            lines.append(f"   🃏 {pos['card']['name']} ({orientation})")
            lines.append(f"   💫 {pos['meaning']}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton
_tarot_deck: Optional[TarotDeck] = None
_tarot_spread: Optional[TarotSpread] = None


def get_tarot_deck() -> TarotDeck:
    """Получить колоду Таро"""
    global _tarot_deck
    if _tarot_deck is None:
        _tarot_deck = TarotDeck()
    return _tarot_deck


def get_tarot_spread() -> TarotSpread:
    """Получить расклад Таро"""
    global _tarot_spread
    if _tarot_spread is None:
        _tarot_spread = TarotSpread()
    return _tarot_spread

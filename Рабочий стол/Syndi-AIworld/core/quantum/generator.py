"""
Quantum Path Generator
Генератор квантовых путей развития

Создает уникальные траектории на основе квантовых вычислений
и профиля пользователя.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random


@dataclass
class QuantumPath:
    """Квантовый путь развития"""
    id: int
    name: str
    description: str
    quantum_state: str
    probability: float
    recommendations: List[str]
    color: str  # Для визуализации


class QuantumPathGenerator:
    """
    Генератор квантовых путей
    
    Создает персонализированные траектории развития
    на основе квантовых принципов
    """
    
    PATH_TEMPLATES = {
        "creative": {
            "name": "Творческий путь",
            "description": "Путь самовыражения и творчества. Фокус на инновациях и искусстве.",
            "color": "#FF6B6B",
            "recommendations": [
                "Пробуйте новые формы творчества",
                "Не бойтесь экспериментировать",
                "Делитесь своими идеями с миром"
            ]
        },
        "analytical": {
            "name": "Аналитический путь",
            "description": "Путь исследования и анализа. Фокус на знаниях и понимании.",
            "color": "#4ECDC4",
            "recommendations": [
                "Углубляйтесь в изучение интересных тем",
                "Развивайте критическое мышление",
                "Делитесь знаниями с другими"
            ]
        },
        "leadership": {
            "name": "Лидерский путь",
            "description": "Путь влияния и руководства. Фокус на развитии других.",
            "color": "#FFD93D",
            "recommendations": [
                "Берите на себя ответственность",
                "Развивайте коммуникационные навыки",
                "Вдохновляйте окружающих"
            ]
        },
        "harmonious": {
            "name": "Гармоничный путь",
            "description": "Путь баланса и единства. Фокус на внутреннем покое.",
            "color": "#95E1D3",
            "recommendations": [
                "Находите время для медитации",
                "Поддерживайте баланс работа/жизнь",
                "Заботьтесь о своем здоровье"
            ]
        },
        "explorer": {
            "name": "Исследовательский путь",
            "description": "Путь открытий и приключений. Фокус на новом опыте.",
            "color": "#A8E6CF",
            "recommendations": [
                "Путешествуйте и открывайте новое",
                "Выходите из зоны комфорта",
                "Записывайте свои открытия"
            ]
        }
    }
    
    def __init__(self):
        self.paths_cache: Dict[str, List[QuantumPath]] = {}
    
    def generate(
        self,
        user_profile: Dict[str, Any],
        num_paths: int = 3
    ) -> List[QuantumPath]:
        """
        Сгенерировать квантовые пути для пользователя
        
        Args:
            user_profile: Профиль пользователя (Big Five, MBTI и т.д.)
            num_paths: Количество путей (1-5)
        
        Returns:
            Список квантовых путей
        """
        # Используем кэш если профиль не изменился
        cache_key = self._get_cache_key(user_profile)
        if cache_key in self.paths_cache:
            return self.paths_cache[cache_key]
        
        # Анализируем профиль
        profile_analysis = self._analyze_profile(user_profile)
        
        # Выбираем подходящие пути
        selected_paths = self._select_paths(profile_analysis, num_paths)
        
        # Генерируем квантовые состояния
        paths = self._generate_quantum_states(selected_paths)
        
        # Кэшируем результат
        self.paths_cache[cache_key] = paths
        
        return paths
    
    def _get_cache_key(self, profile: Dict[str, Any]) -> str:
        """Создать ключ для кэширования"""
        # Используем Big Five как основу для кэша
        big_five = profile.get("big_five", {})
        return f"{big_five.get('openness', 0):.0f}_{big_five.get('conscientiousness', 0):.0f}"
    
    def _analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """Анализировать профиль пользователя"""
        analysis = {
            "creativity": 0.5,
            "analysis": 0.5,
            "leadership": 0.5,
            "harmony": 0.5,
            "exploration": 0.5
        }
        
        # Big Five анализ
        big_five = profile.get("big_five", {})
        if big_five:
            analysis["creativity"] = big_five.get("openness", 50) / 100
            analysis["analysis"] = big_five.get("conscientiousness", 50) / 100
            analysis["leadership"] = big_five.get("extraversion", 50) / 100
            analysis["harmony"] = big_five.get("agreeableness", 50) / 100
            analysis["exploration"] = (100 - big_five.get("neuroticism", 50)) / 100
        
        # MBTI анализ
        mbti = profile.get("mbti", "")
        if mbti:
            mbti_weights = {
                "INTP": {"analysis": 0.9, "creativity": 0.8},
                "ENTP": {"creativity": 0.9, "exploration": 0.8},
                "INTJ": {"analysis": 0.9, "leadership": 0.7},
                "ENTJ": {"leadership": 0.9, "analysis": 0.7},
                "INFJ": {"harmony": 0.9, "creativity": 0.7},
                "ENFJ": {"leadership": 0.9, "harmony": 0.8},
                "INFP": {"creativity": 0.9, "harmony": 0.8},
                "ENFP": {"exploration": 0.9, "creativity": 0.8},
            }
            weights = mbti_weights.get(mbti, {})
            for key, value in weights.items():
                analysis[key] = max(analysis[key], value)
        
        return analysis
    
    def _select_paths(
        self,
        analysis: Dict[str, float],
        num_paths: int
    ) -> List[str]:
        """Выбрать подходящие пути на основе анализа"""
        # Сортируем по релевантности
        sorted_traits = sorted(
            analysis.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Маппинг трейтов на пути
        trait_to_path = {
            "creativity": "creative",
            "analysis": "analytical",
            "leadership": "leadership",
            "harmony": "harmonious",
            "exploration": "explorer"
        }
        
        selected = []
        for trait, _ in sorted_traits[:num_paths]:
            path_key = trait_to_path.get(trait)
            if path_key and path_key not in selected:
                selected.append(path_key)
        
        # Добавляем случайные если не хватает
        all_paths = list(self.PATH_TEMPLATES.keys())
        while len(selected) < num_paths:
            random_path = random.choice(all_paths)
            if random_path not in selected:
                selected.append(random_path)
        
        return selected[:num_paths]
    
    def _generate_quantum_states(
        self,
        path_keys: List[str]
    ) -> List[QuantumPath]:
        """Сгенерировать квантовые состояния для путей"""
        paths = []
        
        for i, path_key in enumerate(path_keys):
            template = self.PATH_TEMPLATES[path_key]
            
            # Генерируем случайное квантовое состояние
            num_qubits = 5
            state = format(random.randint(0, 2**num_qubits - 1), f"0{num_qubits}b")
            
            # Вероятность уменьшается для каждого следующего пути
            probability = max(0.1, 0.5 - i * 0.1 + random.uniform(-0.1, 0.1))
            
            paths.append(QuantumPath(
                id=i + 1,
                name=template["name"],
                description=template["description"],
                quantum_state=state,
                probability=round(probability * 100, 2),
                recommendations=template["recommendations"],
                color=template["color"]
            ))
        
        return paths
    
    def get_path_by_id(
        self,
        paths: List[QuantumPath],
        path_id: int
    ) -> Optional[QuantumPath]:
        """Получить путь по ID"""
        for path in paths:
            if path.id == path_id:
                return path
        return None
    
    def format_path_for_display(self, path: QuantumPath) -> str:
        """Форматировать путь для отображения"""
        return f"""
🔮 {path.name}
━━━━━━━━━━━━━━━━━━━━━━━━
{path.description}

📊 Вероятность: {path.probability}%
⚛️ Квантовое состояние: |{path.quantum_state}⟩

💡 Рекомендации:
{chr(10).join(f"  • {rec}" for rec in path.recommendations)}
"""

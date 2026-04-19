import math
from typing import Dict, Tuple, Any

class MatchingEngine:
    """
    Ядро системы мэтчинга.
    Синтезирует навыки, психотип и эзотерику для поиска идеальной пары.
    """

    def __init__(self):
        # Веса компонентов (можно менять для тюнинга)
        self.WEIGHT_SKILLS = 0.4      # 40% важности за навыки
        self.WEIGHT_PSYCHO = 0.3      # 30% за психо-тип
        self.WEIGHT_ENNEAGRAM = 0.3   # 30% за эннеаграмму

    def calculate_match(self, founder: Dict, candidate: Dict) -> Tuple[float, str]:
        """
        Главный метод. Возвращает (Оценка_0-100, Текст_Оракула).
        """
        # 1. Расчет навыков (Анти-клон)
        skills_score = self._calculate_skills_score(founder.get('skills', {}), candidate.get('skills', {}))
        
        # 2. Расчет психотипа (Комплементарность)
        psycho_score = self._calculate_psycho_score(founder.get('psycho_profile', {}), candidate.get('psycho_profile', {}))
        
        # 3. Расчет Эннеаграммы (Шестерни)
        enneagram_score = self._calculate_enneagram_score(founder.get('enneagram', {}), candidate.get('enneagram', {}))

        # Итоговый скор (взвешенная сумма)
        total_score = (
            (skills_score * self.WEIGHT_SKILLS) +
            (psycho_score * self.WEIGHT_PSYCHO) +
            (enneagram_score * self.WEIGHT_ENNEAGRAM)
        )

        # Генерация текста ИИ
        ai_text = self._ai_oracle(total_score, skills_score, enneagram_score, founder['name'], candidate['name'])

        return total_score, ai_text

    def _calculate_skills_score(self, f_skills: Dict, c_skills: Dict) -> float:
        """
        Ищем уникальные сильные навыки у кандидата, которых нет у фаундера.
        """
        score = 0.0
        found_unique = False
        
        for skill, value in c_skills.items():
            # Если навыка нет у фаундера или он у него слабый (< 0.3), а у кандидата сильный (> 0.7)
            f_val = f_skills.get(skill, 0.0)
            if f_val < 0.3 and value > 0.7:
                score += 1.0
                found_unique = True
        
        # Если нашли хоть один крутой уникальный навык - высокий балл
        # Нормализуем: максимум дадим 100 баллов за этот блок, если навыков много
        return min(score * 50, 100) if found_unique else 10.0

    def _calculate_psycho_score(self, f_psycho: Dict, c_psycho: Dict) -> float:
        """
        Комплементарность: Идеально, если f + c ~= 1.0 (Yin-Yang).
        """
        total_diff = 0.0
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            f_val = f_psycho.get(trait, 0.5)
            c_val = c_psycho.get(trait, 0.5)
            # Ищем сумму близкую к 1.0. Разница (f + c) и 1.0 должна быть минимальной.
            diff = abs((f_val + c_val) - 1.0)
            total_diff += diff
        
        # Средняя разница. 0 = идеально, 1 = ужасно.
        avg_diff = total_diff / len(traits)
        # Конвертируем в评分: 1 - avg_diff -> чем меньше разница, тем выше балл
        return (1.0 - avg_diff) * 100

    def _calculate_enneagram_score(self, f_ennea: Dict, c_ennea: Dict) -> float:
        """
        Механизм шестерней:
        Интеллектуальный центр (5,6,7) + Инстинктивный (8,9,1) + Эмоциональный (2,3,4).
        """
        f_type = f_ennea.get('type', 0)
        c_type = c_ennea.get('type', 0)

        # Группы
        head = {5, 6, 7}
        body = {8, 9, 1}
        heart = {2, 3, 4}

        f_center = self._get_center(f_type, head, body, heart)
        c_center = self._get_center(c_type, head, body, heart)

        if f_center != c_center:
            # Разные центры = отличное зацепление шестерней
            return 100.0
        elif f_type == c_type:
            # Одинаковые типы = конфликт (например, два Босса 8)
            return 20.0
        else:
            # Один центр, но разные типы (нормально, но не вау)
            return 60.0

    def _get_center(self, type_id, head, body, heart):
        if type_id in head: return "head"
        if type_id in body: return "body"
        if type_id in heart: return "heart"
        return "unknown"

    def _ai_oracle(self, total_score: float, s_score: float, e_score: float, f_name: str, c_name: str) -> str:
        """
        Генерирует интерпретацию. Здесь мы эмулируем DeepSeek.
        """
        if total_score > 80:
            return (f"💎 **КОСМИЧЕСКОЕ СОВПАДЕНИЕ!**\n"
                    f"{c_name} — это недостающий пазл для {f_name}. "
                    f"Навыки закрывают бреши ({s_score:.0f}%), а психотипы создают вечный двигатель. "
                    f"Эзотерический резонанс ({e_score:.0f}%) говорит о единстве душ. ")
        elif total_score > 50:
            return (f"⚡ **ХОРОШАЯ КОМАНДА.**\n"
                    f"{f_name} и {c_name} могут работать вместе. "
                    f"Есть потенциал для роста, но придется поработать над коммуникацией. "
                    f"Баланс сил стабильный.")
        else:
            return (f"🛑 **РИСК КОНФЛИКТА.**\n"
                    f"Эта комбинация {f_name} и {c_name} похожа на две шестеренки, которые трутся друг о друга. "
                    f"Рекомендую поискать другого кандидата.")


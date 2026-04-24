"""
EmotionalCore — эмоциональное ядро AI-аватара.
Адаптировано из kristina-revolutionary/emotional_core.py
"""
import random
from datetime import datetime
from typing import Dict, Optional


class EmotionalCore:
    """Эмоциональное состояние аватара — эволюционирует со временем."""

    def __init__(self, big5: Optional[Dict[str, float]] = None):
        # Черты личности (Big Five, 0.0–1.0)
        self.traits = {
            "extraversion":       big5.get("extraversion", 70) / 100 if big5 else 0.7,
            "neuroticism":        big5.get("neuroticism", 40) / 100 if big5 else 0.4,
            "openness":           big5.get("openness", 80) / 100 if big5 else 0.8,
            "agreeableness":      big5.get("agreeableness", 60) / 100 if big5 else 0.6,
            "conscientiousness":  big5.get("conscientiousness", 50) / 100 if big5 else 0.5,
        }

        # Текущее эмоциональное состояние
        self.state = {
            "energy":     0.7,
            "happiness":  0.6,
            "curiosity":  0.8,
            "anxiety":    0.3,
            "creativity": 0.6,
            "irritation": 0.1,
        }
        self.last_update = datetime.now()

    def evolve(self, context: Optional[Dict] = None) -> Dict:
        """Шаг эволюции: время суток + контекст диалога + случайные колебания."""
        hour = datetime.now().hour
        self._apply_circadian(hour)
        if context:
            self._apply_context(context)
        self._fluctuate()
        self._normalize()
        self.last_update = datetime.now()
        return self.get_state()

    def _apply_circadian(self, hour: int):
        if 6 <= hour < 10:
            self.state["energy"] += 0.15
            self.state["curiosity"] += 0.1
        elif 14 <= hour < 17:
            self.state["energy"] -= 0.08
        elif hour >= 22 or hour < 6:
            self.state["energy"] -= 0.15

    def _apply_context(self, context: Dict):
        if context.get("negative_tone"):
            self.state["irritation"] += 0.2
            self.state["happiness"] -= 0.1
        if context.get("positive_tone"):
            self.state["happiness"] += 0.15
            self.state["energy"] += 0.05
        if context.get("complex_question"):
            self.state["curiosity"] += 0.1

    def _fluctuate(self):
        for k in self.state:
            self.state[k] += random.uniform(-0.04, 0.04)

    def _normalize(self):
        for k in self.state:
            self.state[k] = max(0.1, min(1.0, self.state[k]))

    def get_state(self) -> Dict:
        dominant = max(self.state, key=self.state.get)
        return {
            "state": self.state.copy(),
            "traits": self.traits.copy(),
            "dominant_emotion": dominant,
            "mood_description": self._describe_mood(),
            "llm_style_hint": self._llm_hint(),
        }

    def _describe_mood(self) -> str:
        e, h = self.state["energy"], self.state["happiness"]
        if e > 0.7 and h > 0.6:
            return "Энергичная и позитивная"
        if e < 0.4:
            return "Уставшая, нуждается в отдыхе"
        if self.state["curiosity"] > 0.7:
            return "Любопытная, вовлечённая"
        return "Спокойная, сбалансированная"

    def _llm_hint(self) -> str:
        mods = []
        if self.state["energy"] > 0.8:
            mods.append("энергичный тон")
        elif self.state["energy"] < 0.4:
            mods.append("короткие ответы")
        if self.state["curiosity"] > 0.75:
            mods.append("задавай уточняющие вопросы")
        if self.state["irritation"] > 0.6:
            mods.append("будь терпелива")
        return f"Стиль: {', '.join(mods) or 'естественный'}."
# base.py
import os
from typing import Dict, List
from openai import OpenAI


class AIAgent:
    """
    Базовый AI-агент на DeepSeek через openai-совместимый API (openai >= 1.0).
    """

    def __init__(self, system_prompt: str, deepseek_api_key: str):
        self.system_prompt = system_prompt
        self.client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.memories: Dict[str, List[dict]] = {}

    def process_message(self, user_id: str, message: str) -> str:
        """Отправляет сообщение в DeepSeek и возвращает ответ. Хранит историю."""
        if user_id not in self.memories:
            self.memories[user_id] = []

        self.memories[user_id].append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.memories[user_id][-50:]  # ограничиваем контекст
            ]
        )

        answer = response.choices[0].message.content
        self.memories[user_id].append({"role": "assistant", "content": answer})
        return answer

"""
LLM Service for Syndi-AI — Mimo API (OpenAI-compatible).

Mimo совместим с OpenAI API и использует `openai` клиент с кастомным `base_url`.
Ключ читается из env `MIMO_API_KEY`; при его отсутствии `generate_response`
возвращает пустую строку, а вызывающий код уходит на keyword-fallback.
"""
import os
from typing import Dict, List, Optional


class LLMService:
    """Service for LLM interactions (Mimo, OpenAI-compatible)."""

    def __init__(self):
        self.api_key = os.getenv("MIMO_API_KEY", "")
        self.base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo.team/v1")
        self.model = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            return None
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return None
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        return self._client

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = "",
        context: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate response from LLM. Returns "" on missing key / error."""
        client = self._get_client()
        if client is None:
            return ""

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            for m in context:
                role = m.get("role")
                content = m.get("content")
                if role in ("user", "assistant", "system") and isinstance(content, str):
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"LLM request: model={self.model}, messages={len(messages)}")
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
            )
            result = response.choices[0].message.content or ""
            logger.info(f"LLM response: {len(result)} chars")
            return result
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM error: {e}")
            return ""

    async def analyze_personality(self, text: str) -> Dict[str, float]:
        """Analyze personality from text (placeholder)."""
        return {
            "openness": 50.0,
            "conscientiousness": 50.0,
            "extraversion": 50.0,
            "agreeableness": 50.0,
            "neuroticism": 50.0,
        }


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

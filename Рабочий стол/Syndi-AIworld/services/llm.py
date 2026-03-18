"""
LLM Integration Service
Сервис интеграции с языковыми моделями (DeepSeek, OpenAI, etc.)
"""

import os
import json
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp
import asyncio


class LLMProvider(str, Enum):
    """Провайдеры LLM"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"  # Для тестирования


@dataclass
class LLMResponse:
    """Ответ от LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    metadata: Dict[str, Any]


@dataclass
class LLMMessage:
    """Сообщение для LLM"""
    role: str  # system, user, assistant
    content: str


class DeepSeekClient:
    """
    Клиент для DeepSeek API
    
    Документация: https://platform.deepseek.com/
    """
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key не найден. "
                "Установите DEEPSEEK_API_KEY в переменных окружения"
            )
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """
        Отправить запрос к DeepSeek Chat API
        
        Args:
            messages: Список сообщений
            model: Название модели
            temperature: Температура сэмплирования (0-2)
            max_tokens: Максимальное количество токенов
            stream: Использовать потоковую передачу
        
        Returns:
            LLMResponse с ответом модели
        """
        session = await self._get_session()
        
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error {response.status}: {error_text}")
                
                data = await response.json()
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data.get("model", model),
                    usage=data.get("usage", {}),
                    finish_reason=data["choices"][0].get("finish_reason", "unknown"),
                    metadata={
                        "id": data.get("id"),
                        "created": data.get("created")
                    }
                )
                
        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка подключения к DeepSeek API: {str(e)}")
    
    async def chat_completion_stream(
        self,
        messages: List[LLMMessage],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Потоковая генерация ответа
        
        Yields:
            Части ответа по мере генерации
        """
        session = await self._get_session()
        
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with session.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"DeepSeek API error {response.status}: {error_text}")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except (json.JSONDecodeError, KeyError):
                        continue
    
    async def close(self):
        """Закрыть сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class LLMService:
    """
    Сервис для работы с LLM
    
    Поддерживает несколько провайдеров:
    - DeepSeek (основной)
    - OpenAI
    - Mock (для тестирования)
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or self._detect_provider()
        self._client: Optional[Any] = None
    
    def _detect_provider(self) -> LLMProvider:
        """Автоматически определить провайдера по наличию API ключей"""
        if os.getenv("DEEPSEEK_API_KEY"):
            return LLMProvider.DEEPSEEK
        elif os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI
        else:
            return LLMProvider.MOCK
    
    @property
    def client(self):
        """Получить клиент LLM"""
        if self._client is None:
            if self.provider == LLMProvider.DEEPSEEK:
                self._client = DeepSeekClient()
            elif self.provider == LLMProvider.MOCK:
                from agents.base import MockLLMClient
                self._client = MockLLMClient()
            else:
                raise NotImplementedError(f"Провайдер {self.provider} не реализован")
        return self._client
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1500
    ) -> str:
        """
        Сгенерировать ответ от LLM
        
        Args:
            system_prompt: Системный промпт
            user_message: Сообщение пользователя
            context: Контекст разговора
            temperature: Температура
            max_tokens: Максимум токенов
        
        Returns:
            Текст ответа
        """
        messages = [LLMMessage(role="system", content=system_prompt)]
        
        # Добавляем контекст
        if context:
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append(LLMMessage(role=role, content=content))
        
        # Добавляем текущее сообщение
        messages.append(LLMMessage(role="user", content=user_message))
        
        if self.provider == LLMProvider.DEEPSEEK:
            response = await self.client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content
        else:
            # Для мока и других провайдеров
            prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])
            return await self.client.generate(prompt)
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Потоковая генерация ответа
        
        Yields:
            Части ответа
        """
        if self.provider != LLMProvider.DEEPSEEK:
            # Для не-потоковых провайдеров возвращаем целиком
            response = await self.generate_response(
                system_prompt, user_message, context, temperature
            )
            yield response
            return
        
        messages = [LLMMessage(role="system", content=system_prompt)]
        
        if context:
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append(LLMMessage(role=role, content=content))
        
        messages.append(LLMMessage(role="user", content=user_message))
        
        async for chunk in self.client.chat_completion_stream(
            messages=messages,
            temperature=temperature
        ):
            yield chunk
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус сервиса"""
        return {
            "provider": self.provider.value,
            "available": self.provider != LLMProvider.MOCK,
            "client_initialized": self._client is not None
        }


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Получить сервис LLM (singleton)"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def reset_llm_service():
    """Сбросить сервис (для тестирования)"""
    global _llm_service
    _llm_service = None

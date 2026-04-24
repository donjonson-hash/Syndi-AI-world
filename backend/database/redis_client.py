"""
Redis client — кэширование, сессии, pub/sub для аватаров.
Используется для: кэш discover feed, avatar state persistence, rate limiting.

Важно: graceful degradation — если Redis недоступен или пакет не установлен,
приложение продолжает работать без кэша (все функции возвращают None/False).
"""
import os
import logging
from typing import Optional, Any
import json

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_client = None
_redis_init_attempted = False


async def get_redis():
    """Получить Redis клиент (lazy init).

    Возвращает None если Redis недоступен — вызывающий код должен
    корректно обработать этот случай (graceful degradation).
    """
    global _redis_client, _redis_init_attempted
    if _redis_client is not None:
        return _redis_client
    if _redis_init_attempted:
        return None
    _redis_init_attempted = True
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await client.ping()
        _redis_client = client
        logger.info(f"Redis connected: {REDIS_URL}")
    except Exception as e:
        logger.warning(f"Redis unavailable: {e} — running without cache")
        _redis_client = None
    return _redis_client


async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Сохранить значение в кэш (TTL в секундах, default 5 минут)."""
    r = await get_redis()
    if r is None:
        return False
    try:
        await r.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.warning(f"Cache set error for {key}: {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Получить значение из кэша. Возвращает None если ключа нет или Redis недоступен."""
    r = await get_redis()
    if r is None:
        return None
    try:
        val = await r.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.warning(f"Cache get error for {key}: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """Удалить ключ из кэша."""
    r = await get_redis()
    if r is None:
        return False
    try:
        await r.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error for {key}: {e}")
        return False


async def close_redis():
    """Закрыть соединение с Redis (вызывается при shutdown)."""
    global _redis_client, _redis_init_attempted
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception as e:
            logger.warning(f"Redis close error: {e}")
        _redis_client = None
    _redis_init_attempted = False

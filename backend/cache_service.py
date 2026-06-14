"""
Cache Service — Async Redis cache for RAG answers.
Falls back to a no-op in-memory cache when Redis is unavailable.
"""

import logging
import hashlib
import json
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 3600  # 1 hour

_redis = None
_memory_cache: Dict[str, Any] = {}

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis[asyncio] not installed. Using in-memory cache fallback.")


def _cache_key(query: str, namespace: str = "global") -> str:
    raw = f"{namespace}:{query.strip().lower()}"
    return f"specter:rag:{hashlib.md5(raw.encode()).hexdigest()}"


async def get_redis_client():
    global _redis
    if not REDIS_AVAILABLE:
        return None
    if _redis is None:
        try:
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            _redis = aioredis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
            await _redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache: {e}")
            _redis = None
            return None
    return _redis


async def get_cached_answer(query: str, namespace: str = "global") -> Optional[Dict]:
    key = _cache_key(query, namespace)
    client = await get_redis_client()
    if client:
        try:
            data = await client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
    cached = _memory_cache.get(key)
    if cached:
        return cached
    return None


async def set_cached_answer(query: str, answer: Dict, namespace: str = "global", ttl: int = CACHE_TTL_SECONDS):
    key = _cache_key(query, namespace)
    client = await get_redis_client()
    serialized = json.dumps(answer)
    if client:
        try:
            await client.setex(key, ttl, serialized)
            return
        except Exception:
            pass
    _memory_cache[key] = answer
    logger.debug(f"Cached answer for key '{key}' in memory (TTL not enforced without Redis)")


async def invalidate_cache(namespace: str = "global"):
    client = await get_redis_client()
    pattern = f"specter:rag:{namespace}:*"
    if client:
        try:
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await client.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass
    keys_to_delete = [k for k in _memory_cache if k.startswith(f"specter:rag:{namespace}:")]
    for k in keys_to_delete:
        _memory_cache.pop(k, None)
    logger.info(f"Invalidated cache for namespace '{namespace}'")

"""
ECHO OS — Redis Client
Connection pool, pub/sub, and caching utilities with in-memory fallback.
"""

import json
import logging
from typing import Any, Optional, Dict

import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[aioredis.ConnectionPool] = None
_client: Optional[aioredis.Redis] = None
_in_memory_cache: Dict[str, Any] = {}


async def get_redis() -> Optional[aioredis.Redis]:
    """Get or create the Redis client singleton. Returns None if Redis is unreachable."""
    global _pool, _client
    if _client is None:
        try:
            _pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                decode_responses=True,
                socket_timeout=2.0,
            )
            client = aioredis.Redis(connection_pool=_pool)
            await client.ping()
            _client = client
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}). Using in-memory fallback cache.")
            return None
    return _client


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _pool, _client
    if _client:
        try:
            await _client.close()
        except Exception:
            pass
        _client = None
    if _pool:
        try:
            await _pool.disconnect()
        except Exception:
            pass
        _pool = None


# ── Cache Utilities ──


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a JSON-serializable value in Redis or in-memory fallback."""
    client = await get_redis()
    serialized = json.dumps(value, default=str)
    if client:
        try:
            await client.setex(key, ttl, serialized)
            return
        except Exception:
            pass
    _in_memory_cache[key] = serialized


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value from Redis or in-memory fallback."""
    client = await get_redis()
    data = None
    if client:
        try:
            data = await client.get(key)
        except Exception:
            pass
    if data is None:
        data = _in_memory_cache.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_delete(key: str) -> None:
    """Delete a cached value."""
    client = await get_redis()
    if client:
        try:
            await client.delete(key)
        except Exception:
            pass
    _in_memory_cache.pop(key, None)


# ── Pub/Sub ──


async def publish_event(channel: str, data: dict) -> None:
    """Publish an event to a Redis channel."""
    client = await get_redis()
    if client:
        try:
            await client.publish(channel, json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"Redis publish failed: {e}")


# ── Session Store ──


async def store_user_session(user_id: str, session_data: dict, ttl: int = 86400) -> None:
    """Store user session data."""
    await cache_set(f"session:{user_id}", session_data, ttl)


async def get_user_session(user_id: str) -> Optional[dict]:
    """Retrieve user session data."""
    return await cache_get(f"session:{user_id}")


async def clear_user_session(user_id: str) -> None:
    """Clear user session data."""
    await cache_delete(f"session:{user_id}")

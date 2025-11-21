"""
Redis caching layer for CodeRenew API
Provides async caching for API responses and database queries
"""
import json
import hashlib
import logging
from typing import Optional, Any, Callable, TypeVar
from functools import wraps
import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Global Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[aioredis.Redis] = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
    return _redis_pool


async def get_redis_client() -> aioredis.Redis:
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None:
        pool = await get_redis_pool()
        _redis_client = aioredis.Redis(connection_pool=pool)
    return _redis_client


async def close_redis() -> None:
    """Close Redis connections"""
    global _redis_client, _redis_pool
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


class CacheService:
    """Redis caching service with namespace support"""

    def __init__(self, namespace: str = "coderenew"):
        self.namespace = namespace
        self._enabled = settings.REDIS_ENABLED

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key"""
        return f"{self.namespace}:{key}"

    def _hash_key(self, *args, **kwargs) -> str:
        """Create a hash key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._enabled:
            return None

        try:
            client = await get_redis_client()
            value = await client.get(self._make_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self._enabled:
            return False

        try:
            client = await get_redis_client()
            serialized = json.dumps(value, default=str)
            ttl = ttl or settings.REDIS_DEFAULT_TTL
            await client.set(self._make_key(key), serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self._enabled:
            return False

        try:
            client = await get_redis_client()
            await client.delete(self._make_key(key))
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self._enabled:
            return 0

        try:
            client = await get_redis_client()
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in client.scan_iter(match=full_pattern):
                keys.append(key)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._enabled:
            return False

        try:
            client = await get_redis_client()
            return await client.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.warning(f"Cache exists error: {e}")
            return False


# Global cache instance
cache = CacheService()


# Cache for scan results
scan_cache = CacheService(namespace="coderenew:scans")

# Cache for site data
site_cache = CacheService(namespace="coderenew:sites")

# Cache for user data
user_cache = CacheService(namespace="coderenew:users")


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    cache_service: CacheService = None
):
    """
    Decorator for caching async function results

    Usage:
        @cached(ttl=600, key_prefix="scan_result")
        async def get_scan_result(scan_id: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            service = cache_service or cache

            # Build cache key
            func_name = func.__name__
            key_hash = service._hash_key(*args, **kwargs)
            cache_key = f"{key_prefix}:{func_name}:{key_hash}" if key_prefix else f"{func_name}:{key_hash}"

            # Try to get from cache
            cached_value = await service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await service.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss, stored: {cache_key}")

            return result
        return wrapper
    return decorator


async def invalidate_scan_cache(scan_id: str) -> None:
    """Invalidate all cache entries for a specific scan"""
    await scan_cache.delete_pattern(f"*{scan_id}*")


async def invalidate_site_cache(site_id: str) -> None:
    """Invalidate all cache entries for a specific site"""
    await site_cache.delete_pattern(f"*{site_id}*")


async def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache entries for a specific user"""
    await user_cache.delete_pattern(f"*{user_id}*")

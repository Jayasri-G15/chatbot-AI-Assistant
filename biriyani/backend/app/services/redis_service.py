import logging
from typing import Optional, Any

try:
    import redis
except ImportError:
    redis = None

from app.core.config import settings

logger = logging.getLogger("app.redis")

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[Any]:
    """
    Get or initialize Redis connection pool with connection timeout.
    Returns None if Redis is disabled, uninstalled, or unreachable.
    """
    global _redis_client
    if not settings.redis_enabled or redis is None:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=False,
            )
        except Exception as exc:
            logger.warning(f"Failed to initialize Redis client: {exc}")
            _redis_client = None

    return _redis_client


def redis_health_check() -> dict[str, Any]:
    """
    Check Redis ping connection status safely without throwing exceptions.
    """
    client = get_redis_client()
    if client is None:
        return {"status": "disabled", "connected": False}
    try:
        ping = client.ping()
        return {"status": "ok" if ping else "error", "connected": bool(ping)}
    except Exception as exc:
        logger.warning(f"Redis health check failed: {exc}")
        return {"status": "unavailable", "connected": False, "error": str(exc)}


def redis_get(key: str) -> Optional[str]:
    """
    Get cached string value by key. Returns None on cache miss or Redis error.
    """
    client = get_redis_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except Exception as exc:
        logger.warning(f"Redis get failed for key '{key}': {exc}")
        return None


def redis_set(key: str, value: str, ttl_seconds: int = 300) -> bool:
    """
    Set cache string value with explicit TTL.
    """
    client = get_redis_client()
    if client is None:
        return False
    try:
        return bool(client.set(name=key, value=value, ex=ttl_seconds))
    except Exception as exc:
        logger.warning(f"Redis set failed for key '{key}': {exc}")
        return False


def redis_delete(key: str) -> bool:
    """
    Delete a key from Redis.
    """
    client = get_redis_client()
    if client is None:
        return False
    try:
        return bool(client.delete(key))
    except Exception as exc:
        logger.warning(f"Redis delete failed for key '{key}': {exc}")
        return False


def redis_exists(key: str) -> bool:
    """
    Check if a key exists in Redis.
    """
    client = get_redis_client()
    if client is None:
        return False
    try:
        return bool(client.exists(key))
    except Exception as exc:
        logger.warning(f"Redis exists failed for key '{key}': {exc}")
        return False

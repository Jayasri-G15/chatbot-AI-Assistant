import time
from collections import defaultdict, deque
from app.services.redis_service import get_redis_client

MAX_REQUESTS = 10
WINDOW_SECONDS = 60

_hits: dict[str, deque[float]] = defaultdict(deque)


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after


def check_rate_limit(key: str, max_requests: int = MAX_REQUESTS, window_seconds: int = WINDOW_SECONDS) -> None:
    # Try Redis rate limit first
    client = get_redis_client()
    if client is not None:
        try:
            rkey = f"ratelimit:{key}"
            current = client.incr(rkey)
            if current == 1:
                client.expire(rkey, window_seconds)
            if current > max_requests:
                ttl = client.ttl(rkey)
                retry_after = ttl if ttl > 0 else window_seconds
                raise RateLimitExceeded(retry_after)
            return
        except RateLimitExceeded:
            raise
        except Exception:
            # Fall back seamlessly to in-memory check if Redis throws error
            pass

    # In-memory sliding-window fallback
    now = time.monotonic()
    hits = _hits[key]

    while hits and now - hits[0] > window_seconds:
        hits.popleft()

    if len(hits) >= max_requests:
        retry_after = max(1, int(window_seconds - (now - hits[0])))
        raise RateLimitExceeded(retry_after)

    hits.append(now)

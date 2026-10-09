import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from app.services.redis_service import (
    get_redis_client,
    redis_get,
    redis_set,
    redis_delete,
    redis_exists,
    redis_health_check,
)
from app.services.rate_limit_service import check_rate_limit, RateLimitExceeded

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_ready_endpoint():
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "ok"
    assert "redis" in data


def test_health_no_secret_leakage():
    res1 = client.get("/health")
    res2 = client.get("/ready")

    str1 = str(res1.json())
    str2 = str(res2.json())

    for token in ["password", "secret", "jwt", "api_key", "postgres://", "redis://"]:
        assert token not in str1
        assert token not in str2


def test_redis_graceful_degradation(monkeypatch):
    # Simulate Redis disabled
    monkeypatch.setattr(settings, "redis_enabled", False)

    assert redis_get("test_key") is None
    assert redis_set("test_key", "val") is False
    assert redis_delete("test_key") is False
    assert redis_exists("test_key") is False

    health = redis_health_check()
    assert health["connected"] is False
    assert health["status"] == "disabled"


def test_rate_limiter_fallback():
    key = "test_user_infra_limit"
    # Execute check_rate_limit multiple times under limit
    for _ in range(5):
        check_rate_limit(key, max_requests=10, window_seconds=60)

    # Exceed rate limit
    with pytest.raises(RateLimitExceeded):
        check_rate_limit(key, max_requests=5, window_seconds=60)

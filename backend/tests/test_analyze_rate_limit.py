from app.services.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_allows_requests_under_limit():
    limiter = InMemoryRateLimiter()
    decision = limiter.check("user:123", limit=3, window_seconds=60)
    assert decision.allowed is True
    assert decision.retry_after_seconds == 0


def test_rate_limiter_blocks_requests_exceeding_limit():
    current_time = 1000.0

    def time_provider():
        return current_time

    limiter = InMemoryRateLimiter(time_provider=time_provider)

    assert limiter.check("user:123", limit=2, window_seconds=60).allowed is True
    assert limiter.check("user:123", limit=2, window_seconds=60).allowed is True

    blocked = limiter.check("user:123", limit=2, window_seconds=60)
    assert blocked.allowed is False
    assert blocked.retry_after_seconds == 60


def test_rate_limiter_isolates_different_keys():
    limiter = InMemoryRateLimiter()

    assert limiter.check("user:1", limit=1, window_seconds=60).allowed is True
    assert limiter.check("user:1", limit=1, window_seconds=60).allowed is False

    # user:2 is unaffected by user:1 limit
    assert limiter.check("user:2", limit=1, window_seconds=60).allowed is True


def test_rate_limiter_resets_after_window():
    current_time = 100.0

    def time_provider():
        return current_time

    limiter = InMemoryRateLimiter(time_provider=time_provider)
    assert limiter.check("client:ip", limit=1, window_seconds=10).allowed is True
    assert limiter.check("client:ip", limit=1, window_seconds=10).allowed is False

    current_time = 111.0  # past window
    assert limiter.check("client:ip", limit=1, window_seconds=10).allowed is True


from collections import deque
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic
from typing import Callable


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


class InMemoryRateLimiter:
    """Rate limiter tối giản cho MVP, chỉ giữ metadata request và không lưu nội dung chat."""

    def __init__(self, time_provider: Callable[[], float] = monotonic):
        self._time_provider = time_provider
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitDecision:
        if limit <= 0 or window_seconds <= 0:
            return RateLimitDecision(allowed=True)

        now = self._time_provider()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = self._requests.setdefault(key, deque())
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= limit:
                retry_after = max(1, ceil(window_seconds - (now - timestamps[0])))
                return RateLimitDecision(allowed=False, retry_after_seconds=retry_after)

            timestamps.append(now)
            return RateLimitDecision(allowed=True)

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


analyze_rate_limiter = InMemoryRateLimiter()

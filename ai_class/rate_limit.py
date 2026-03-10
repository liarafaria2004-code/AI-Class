"""In-memory rate limiting for model-backed endpoints."""

from __future__ import annotations

import time
from collections import defaultdict, deque


class RateLimitExceeded(Exception):
    pass


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self._calls: dict[str, deque[float]] = defaultdict(deque)

    def check(self, identity: str) -> None:
        now = time.time()
        window_start = now - 60
        bucket = self._calls[identity]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.limit_per_minute:
            raise RateLimitExceeded("Rate limit exceeded")
        bucket.append(now)

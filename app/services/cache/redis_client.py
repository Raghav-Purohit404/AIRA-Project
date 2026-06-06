"""Redis-compatible cache with transparent in-memory fallback."""

from __future__ import annotations

import json
import os
from threading import RLock
from time import monotonic
from typing import Any


class RedisCache:
    """Expose JSON cache operations without requiring a live Redis server."""

    def __init__(self, url: str | None = None, connect: bool = True) -> None:
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Any = None
        self._memory: dict[str, tuple[str, float | None]] = {}
        self._lock = RLock()
        if connect:
            self._connect()

    @property
    def backend(self) -> str:
        """Return the active cache backend."""
        return "redis" if self._client is not None else "memory"

    def _connect(self) -> None:
        """Attempt a short Redis connection and fall back silently."""
        try:
            import redis

            client = redis.Redis.from_url(
                self.url,
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.5,
            )
            client.ping()
            self._client = client
        except Exception:
            self._client = None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """JSON serialize and cache a value."""
        payload = json.dumps(value, separators=(",", ":"), default=str)
        if self._client is not None:
            try:
                return bool(self._client.set(key, payload, ex=ttl))
            except Exception:
                self._client = None
        expires_at = monotonic() + ttl if ttl is not None else None
        with self._lock:
            self._memory[key] = (payload, expires_at)
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """Return a deserialized value from Redis or memory."""
        payload: str | None
        if self._client is not None:
            try:
                payload = self._client.get(key)
                return json.loads(payload) if payload is not None else default
            except Exception:
                self._client = None
        with self._lock:
            entry = self._memory.get(key)
            if entry is None:
                return default
            payload, expires_at = entry
            if expires_at is not None and expires_at <= monotonic():
                del self._memory[key]
                return default
        return json.loads(payload)

    def delete(self, key: str) -> bool:
        """Delete a cached key."""
        if self._client is not None:
            try:
                return bool(self._client.delete(key))
            except Exception:
                self._client = None
        with self._lock:
            return self._memory.pop(key, None) is not None

    async def aget(self, key: str, default: Any = None) -> Any:
        """Async-compatible get operation."""
        return self.get(key, default)

    async def aset(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Async-compatible set operation."""
        return self.set(key, value, ttl)

    async def adelete(self, key: str) -> bool:
        """Async-compatible delete operation."""
        return self.delete(key)


redis_cache = RedisCache()

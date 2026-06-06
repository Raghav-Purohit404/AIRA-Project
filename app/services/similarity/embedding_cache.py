"""Thread-safe in-memory embedding cache with Redis-compatible semantics."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic


@dataclass
class _CacheEntry:
    vector: list[float]
    expires_at: float | None


class EmbeddingCache:
    """Cache embedding vectors while external cache infrastructure is optional."""

    def __init__(self, default_ttl: float | None = None) -> None:
        self._entries: dict[str, _CacheEntry] = {}
        self._lock = RLock()
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> list[float] | None:
        """Return a cached vector, excluding expired entries."""
        with self._lock:
            entry = self._entries.get(key)
            if entry is None or (entry.expires_at is not None and entry.expires_at <= monotonic()):
                if entry is not None:
                    del self._entries[key]
                self._misses += 1
                return None
            self._hits += 1
            return list(entry.vector)

    def set(self, key: str, embedding: list[float], ttl: float | None = None) -> None:
        """Store a defensive copy of an embedding vector."""
        effective_ttl = self.default_ttl if ttl is None else ttl
        expires_at = monotonic() + effective_ttl if effective_ttl is not None else None
        with self._lock:
            self._entries[key] = _CacheEntry(list(embedding), expires_at)

    def exists(self, key: str) -> bool:
        """Return whether a live cache entry exists."""
        return self.get(key) is not None

    def invalidate(self, key: str) -> bool:
        """Delete one cache entry and report whether it existed."""
        with self._lock:
            return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        """Invalidate every cached embedding."""
        with self._lock:
            self._entries.clear()

    def statistics(self) -> dict[str, int | float]:
        """Return cache size, hit counts, and hit rate."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._entries),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 4) if total else 0.0,
            }

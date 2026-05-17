from typing import Dict


class EmbeddingCache:
    def __init__(self):
        self.cache: Dict[str, list] = {}

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, embedding):
        self.cache[key] = embedding

    def exists(self, key: str) -> bool:
        return key in self.cache

    def clear(self):
        self.cache.clear()
"""Vector similarity and embedding evaluation metrics."""

from __future__ import annotations

import math
from collections.abc import Sequence


def cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    """Return cosine similarity for equal-length vectors."""
    if len(vector_a) != len(vector_b) or not vector_a:
        raise ValueError("Vectors must be non-empty and have equal dimensions.")
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / (magnitude_a * magnitude_b)))


def euclidean_distance(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    """Return Euclidean distance for equal-length vectors."""
    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have equal dimensions.")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vector_a, vector_b)))


def normalize_vector(vector: Sequence[float]) -> list[float]:
    """Return an L2-normalized vector."""
    magnitude = math.sqrt(sum(value * value for value in vector))
    return [float(value) / magnitude for value in vector] if magnitude else [float(value) for value in vector]


def mean_similarity(pairs: Sequence[tuple[Sequence[float], Sequence[float]]]) -> float:
    """Return mean cosine similarity for vector pairs."""
    if not pairs:
        return 0.0
    return round(sum(cosine_similarity(first, second) for first, second in pairs) / len(pairs), 4)

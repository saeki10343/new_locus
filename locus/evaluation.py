"""Evaluation metrics for bug localization."""

from typing import List


def mrr(ranks: List[int]) -> float:
    """Mean reciprocal rank."""
    return sum(1 / r for r in ranks if r > 0) / len(ranks)


def top_n(ranks: List[int], n: int) -> float:
    """Percentage of items with rank <= n."""
    hits = sum(1 for r in ranks if 0 < r <= n)
    return hits / len(ranks)


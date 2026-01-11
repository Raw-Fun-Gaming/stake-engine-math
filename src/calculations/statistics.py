"""Statistical utility functions for slot game simulations.

This module provides functions for:
- Random outcome selection from weighted distributions
- Statistical calculations (mean, standard deviation, median)
- Distribution normalization
"""

from __future__ import annotations

import random
from typing import Any


def get_random_outcome(
    distribution: dict[Any, float], totalWeight: float | None = None
) -> Any:
    """Returns a random value from a weighted distribution.

    Selects a value from the distribution dictionary based on weights using
    cumulative probability. Commonly used for selecting reel strips, scatter
    counts, multiplier values, etc.

    Args:
        distribution: Dict mapping values to their weights {value: weight, ...}
        totalWeight: Optional pre-calculated sum of all weights (for performance)

    Returns:
        A value from the distribution keys, selected based on weights

    Raises:
        AssertionError: If distribution is not a dict
        Exception: If no value is selected (should not happen with valid weights)

    Example:
        >>> dist = {"A": 10, "B": 20, "C": 70}
        >>> outcome = get_random_outcome(dist)  # 70% chance of "C"
    """
    assert isinstance(distribution, dict), "distribution must be of type: dict "
    if totalWeight is None:
        totalWeight = sum(distribution.values())
    roll: float = random.uniform(0, totalWeight)
    cumulative: float = 0.0
    for value, weight in distribution.items():
        cumulative += weight
        if cumulative >= roll:
            return value

    raise Exception("error drawing item from distribution")


def get_mean_std_median(dist: dict[float, int | float]) -> tuple[float, float, float]:
    """Calculate mean, standard deviation, and median from a win distribution.

    Args:
        dist: Dict mapping win amounts to their frequencies {win: count, ...}

    Returns:
        Tuple of (mean, standard_deviation, median)

    Example:
        >>> wins = {10.0: 100, 20.0: 50, 50.0: 10}
        >>> mean, std, median = get_mean_std_median(wins)
    """
    total: float = 0.0
    count: int = 0
    std_total: float = 0.0
    for win in dist:
        total += win * dist[win]
        count += int(dist[win])

    mean: float = total / count if count > 0 else 0.0
    median: float = 0.0
    sorted_dist_keys: list[float] = list(dist.keys())
    sorted_dist_keys.sort()
    loop_count: int = 0
    has_median: bool = False
    for win in sorted_dist_keys:
        loop_count += int(dist[win])
        std_total += ((win - mean) ** 2) * dist[win] / count

        if (not has_median) and loop_count > count / 2:
            median = win
            has_median = True

    return mean, std_total**0.5, median


def normalize(distribution: dict[Any, float]) -> None:
    """Normalize distribution weights to sum to 1.0.

    Modifies the distribution dict in-place by dividing each weight by the
    total sum of all weights.

    Args:
        distribution: Dict mapping values to weights (modified in-place)

    Example:
        >>> dist = {"A": 10, "B": 20, "C": 70}
        >>> normalize(dist)
        >>> # dist is now {"A": 0.1, "B": 0.2, "C": 0.7}
    """
    count: float = 0.0
    for key in distribution:
        count += distribution[key]

    for key in distribution:
        distribution[key] = distribution[key] / count

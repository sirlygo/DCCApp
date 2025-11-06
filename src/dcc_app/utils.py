"""Helper utilities for dice rolling and user interactions."""

from __future__ import annotations

import random
from typing import Iterable, Tuple


def roll_dice(formula: str) -> int:
    """Roll dice using NdM+K notation.

    Examples
    --------
    >>> random.seed(1)
    >>> roll_dice("2d6+1")
    8
    """

    parts = formula.lower().replace(" ", "").split("d")
    if len(parts) != 2:
        raise ValueError(f"Invalid dice formula: {formula!r}")

    num, rest = parts
    num_dice = int(num) if num else 1

    modifier = 0
    if "+" in rest:
        sides_str, modifier_str = rest.split("+", 1)
        modifier = int(modifier_str)
    elif "-" in rest:
        sides_str, modifier_str = rest.split("-", 1)
        modifier = -int(modifier_str)
    else:
        sides_str = rest

    sides = int(sides_str)
    total = sum(random.randint(1, sides) for _ in range(num_dice))
    return total + modifier


def clamp(value: int, lower: int, upper: int) -> int:
    """Clamp *value* between *lower* and *upper*."""

    return max(lower, min(upper, value))


def choose_weighted(options: Iterable[Tuple[float, str]]) -> str:
    """Randomly pick from weighted (weight, value) pairs."""

    items = list(options)
    total_weight = sum(weight for weight, _ in items)
    threshold = random.uniform(0, total_weight)
    cumulative = 0.0
    for weight, value in items:
        cumulative += weight
        if cumulative >= threshold:
            return value
    return items[-1][1]

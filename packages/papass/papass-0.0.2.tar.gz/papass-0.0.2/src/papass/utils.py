from collections.abc import Iterable
from functools import reduce


def digits_to_value(base: int, digits: Iterable[int]) -> int:
    """Compute the integer with the given digits in base.

    Example:
    >>> digits_to_value(10, [1, 2, 3])
    123
    """
    assert 1 < base
    assert all(0 <= d < base for d in digits)
    return reduce(lambda acc, r: base * acc + r, digits, 0)


def rolls_to_value(num_sides: int, rolls: Iterable[int]) -> int:
    """Compute the integer corresponding to the given dice rolls.

    Example:
    >>> rolls_to_value(6, [5, 3])  # 6*(5-1) + (3-1)
    26
    """
    digits = [r - 1 for r in rolls]
    return digits_to_value(num_sides, digits)

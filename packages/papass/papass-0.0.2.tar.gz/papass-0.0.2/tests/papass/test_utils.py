import pytest
from papass.utils import digits_to_value, rolls_to_value


@pytest.mark.parametrize(
    "base, digits, expected",
    [
        (10, [9, 2, 3], 923),
        (2, [0, 1, 1], 3),
        (7, [3, 1, 6], 3 * 49 + 1 * 7 + 6 * 1),
    ],
)
def test_digits_to_value(base, digits, expected):
    assert expected == digits_to_value(base, digits)


@pytest.mark.parametrize(
    "num_sides, rolls",
    [
        (6, [5, 1, 3, 6]),
        (10, [10, 1, 8]),
        (20, [20, 19, 3, 1, 17]),
    ],
)
def test_rolls_to_value(num_sides, rolls):
    expected = digits_to_value(num_sides, [r - 1 for r in rolls])
    assert expected == rolls_to_value(num_sides, rolls)

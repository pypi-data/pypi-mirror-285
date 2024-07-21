import pytest

from .cycle_rng import CycleRng


@pytest.fixture
def cycle_rng():
    return CycleRng(range(10, 13))


@pytest.mark.parametrize(
    "upper,expected_output",
    [
        (100, [10, 11, 12, 10, 11, 12, 10]),
        (10, [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1]),
    ],
)
def test_cycle_rng(cycle_rng, upper, expected_output):
    output = [cycle_rng.randbelow(upper) for _ in range(len(expected_output))]
    assert output == expected_output

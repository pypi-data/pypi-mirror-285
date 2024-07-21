import pytest
from papass.random.base import RandomNumberGeneratorBase

from tests.utils.cycle_rng import CycleRng


def get_cycle():
    return [0, 3, 2, 1]


class TestRandomNumberGeneratorBase:
    @pytest.fixture(scope="class")
    def cycle_rng(self) -> RandomNumberGeneratorBase:
        return CycleRng(get_cycle())

    @pytest.mark.parametrize("i", range(4))
    def test_choice_uses_randbelow_as_desired(self, i, cycle_rng):
        items = [10, 11, 12, 13]
        cycle = get_cycle()

        assert cycle_rng.choice(items) == items[cycle[i]]

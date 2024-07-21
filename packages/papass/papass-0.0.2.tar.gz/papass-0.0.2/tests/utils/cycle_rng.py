from collections.abc import Iterator, Sequence

from papass.random.base import RandomNumberGeneratorBase


class CycleRng(RandomNumberGeneratorBase):
    """A "random" number generator producing pre-determined output.

    See tests for this class on how it is supposed to work.
    """

    _cycle: Iterator[int]

    def __init__(self, cycle: Sequence[int]):
        assert cycle, "Cycle must not be empty."

        def _cycler() -> Iterator[int]:
            i = -1
            while True:
                yield cycle[(i := (i + 1) % len(cycle))]

        self._cycle = _cycler()

    def randbelow(self, upper: int) -> int:
        """Return a not-so-random integer from [0, upper)."""
        return next(self._cycle) % upper

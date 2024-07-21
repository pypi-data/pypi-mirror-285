import secrets

from .base import RandomNumberGeneratorBase


class SystemRng(RandomNumberGeneratorBase):
    """Random number generator using the most secure rng of the operating system."""

    def randbelow(self, upper: int) -> int:
        return secrets.randbelow(upper)

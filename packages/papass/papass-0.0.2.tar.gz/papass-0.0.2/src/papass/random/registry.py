from typing import Type

from .base import RandomNumberGeneratorBase
from .dice import DiceRng
from .system import SystemRng

_rng_registry: dict[str, tuple[Type[RandomNumberGeneratorBase], dict[str, str]]] = dict(
    # This maps the random_source to two things:
    # 1. A ctor for an rng.
    # 2. A dict mapping the __init__ options of the rng to their corresponding command line options.
    system=(SystemRng, {}),
    dice=(DiceRng, {"num_sides": "dice_sides"}),
)


def default_random_source() -> str:
    """Default value for --random-source."""
    # NOTE: dicts are ordered by insertion order.
    return list(_rng_registry.keys())[0]


def available_random_sources() -> list[str]:
    """Get a list of all valid values for --random-source."""
    return list(_rng_registry.keys())


def available_random_sources_str() -> str:
    """A string representing all valid values for --random-source."""
    return ", ".join(f"'{s}'" for s in available_random_sources())


def get_rng(random_source: str, **possible_options) -> RandomNumberGeneratorBase:
    """Get a random number generator of the given source.

    The `possible_options` should contain all command line options which are relevant for
    the random_source. It is OK if it contains superfluous options which are not relevant
    to the rng (those are ignored)
    """
    assert (
        random_source in _rng_registry
    ), f"Unknown random source `{random_source}`. Use one of {available_random_sources_str()}."
    RngCls, args = _rng_registry[random_source]
    return RngCls(**{kw: possible_options[o] for kw, o in args.items()})

from dataclasses import dataclass

import click

from papass.utils import rolls_to_value

from .base import RandomNumberGeneratorBase


@dataclass
class DiceFrame:
    upper_multiple: int
    required_num_rolls: int


class DiceRng(RandomNumberGeneratorBase):
    """Random number generator relying on the user to throw physical dice."""

    def __init__(self, *, num_sides: int = 6, required_success_probability: float = 0.99):
        """Create a `DiceRng`.

        :param num_sides: Number of sides of the dice.
        :param required_success_probability: The minimal required probability that
            `randbelow` does not reject a roll. If `upper` is a power of `num_sides` this
            probability is always 100%. But in general the number of required rolls
            increases with this probability.
        """
        assert num_sides > 1, f"num_sides must be at least 1, got {num_sides}"
        assert (
            0 <= required_success_probability < 1.0
        ), f"required_success_probability must be >= 0 and < 1.0. Got {required_success_probability}."

        self._num_sides = num_sides
        self._required_success_probability = required_success_probability

    def randbelow(self, upper: int) -> int:
        """Generate random integers `i` with `0 <= i < upper`.

        If the dice are fair (all sides occur with the same probability) and the rolls are
        independent the distriubtion of `i` is uniform.
        """
        frame = self._compute_frame(upper)
        required_num_rolls = frame.required_num_rolls
        upper_multiple = frame.upper_multiple

        result = None
        count = 0
        while result is None:
            assert count < 20, "Too many wrong inputs."

            rolls = self._next_rolls(required_num_rolls)

            if rolls is None:
                count += 1
                continue

            result = rolls_to_value(self._num_sides, rolls)

            if result >= upper_multiple:
                count = 0
                click.echo("Rejected. Try again!")
                result = None
                continue

            result = result % upper

        return result

    def _compute_frame(self, upper: int) -> DiceFrame:
        return compute_dice_frame(
            upper=upper,
            num_sides=self._num_sides,
            required_success_probability=self._required_success_probability,
        )

    def _next_rolls(self, required_num_rolls: int) -> list[int] | None:
        """Get rolls from user."""
        return query_stdin_for_dice(
            num_sides=self._num_sides, required_num_rolls=required_num_rolls
        )


def query_stdin_for_dice(*, num_sides: int, required_num_rolls: int) -> list[int] | None:
    """Query stdin for desired number of dice rolls.

    Return `None` if user gives invalid input.
    """
    user_input = input(f"Roll at least {required_num_rolls} dice: ")
    rolls = _parse_stdin(
        user_input, num_sides=num_sides, required_num_rolls=required_num_rolls
    )
    return rolls


def compute_dice_frame(
    *, num_sides: int, upper: int, required_success_probability: float
) -> DiceFrame:
    """Computes the dice frame.

    The dice frame contains information on how to turn dice rolls into numbers from an
    interval [0, upper) with a uniform distribution.

    We assume that the dice rolls themselves is (at least approximately) uniform and
    independent.
    """
    required_num_rolls = 1
    upper_dice = num_sides
    upper_multiple = (upper_dice // upper) * upper

    def success_probability_to_low() -> bool:
        prob = upper_multiple / upper_dice
        return prob < required_success_probability

    while upper_dice < upper or success_probability_to_low():
        required_num_rolls += 1
        upper_dice *= num_sides
        upper_multiple = (upper_dice // upper) * upper

    return DiceFrame(
        upper_multiple=upper_multiple,
        required_num_rolls=required_num_rolls,
    )


def _parse_stdin(
    user_input: str, *, num_sides: int, required_num_rolls: int
) -> list[int] | None:
    """Parse user input as a list of dice rolls.

    Returns `None` if input is invalid.

    Example:
    >>> _parse_stdin("2 3 5", num_sides=6, required_num_rolls=3)
    [2, 3, 5]
    """
    try:
        rolls = [int(r) for r in user_input.split()]
    except ValueError:
        click.echo(
            "Invalid. Require a space-separated list of integers (like: 1 3 2). Roll again!"
        )
        return None

    if len(rolls) < required_num_rolls:
        click.echo(f"Got only {len(rolls)} rolls, need {required_num_rolls}. Roll again!")
        return None

    if not all(1 <= r <= num_sides for r in rolls):
        click.echo(f"Some rolls are not between 1 and {num_sides}. Roll again!")
        return None

    return rolls

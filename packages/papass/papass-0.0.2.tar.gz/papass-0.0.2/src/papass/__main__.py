from pathlib import Path

import click

from papass import (
    PhraseGenerator,
    WordList,
)
from papass.random import (
    available_random_sources_str,
    default_random_source,
    get_rng,
)


@click.command()
@click.option(
    "--count",
    "-c",
    type=int,
    required=True,
    help="Number of words to generate.",
)
@click.option(
    "--random-source",
    "-r",
    default=f"{default_random_source()}",
    help=f"Source of randomness (default: '{default_random_source()}',"
    f" available: {available_random_sources_str()}).",
)
@click.option(
    "--wordlist-file",
    "-w",
    required=True,
    help="A file with a new-line-separated list of words.",
)
@click.option(
    "--delimiter",
    "-d",
    default=" ",
    help="Separator between the words (default: ' ').",
)
@click.option(
    "--min-word-size",
    "--minw",
    type=int,
    default=1,
    help="Filter out words which are shorter than this (default: 1).",
)
@click.option(
    "--max-word-size",
    "--maxw",
    type=int,
    help="Filter out words which are longer than this (default: no limit).",
)
@click.option(
    "--dice-sides",
    "--ds",
    type=int,
    default=6,
    help="Number of sides of dice (default: 6).",
)
@click.version_option()
def cli(
    count,
    random_source,
    wordlist_file,
    delimiter,
    min_word_size,
    max_word_size,
    dice_sides,
):
    """Create a passphrase."""

    try:
        rng = get_rng(random_source, dice_sides=dice_sides)

        wordlist = WordList.from_file(
            Path(wordlist_file),
            min_word_size=min_word_size,
            max_word_size=max_word_size,
        )

        phrase_generator = PhraseGenerator(
            wordlist=wordlist, rng=rng, delimiter=delimiter
        )
        result = phrase_generator.get_phrase(count)
    except AssertionError as error:
        click.secho(f"ERROR: {error}", fg="red")
        click.echo("Try again!")
        return

    click.echo(f"Phrase: {result.phrase}")
    click.echo(f"Entropy: {result.entropy:.6}")

    if not result.entropy_is_guaranteed:
        click.secho(
            "WARNING: Entropy might be slightly lower than estimated. "
            "This can occur for example if the delimiter is contained "
            "in one of the words.",
            fg="yellow",
        )


if __name__ == "__main__":
    cli()

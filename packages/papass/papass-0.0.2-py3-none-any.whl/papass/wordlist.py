from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import overload


class WordList(Sequence[str]):
    """Represents an sorted sequence of unique words.

    Internally the list of words is deduplicated and sorted (via `sorted`).

    # Example

    >>> wordlist = WordList(["c", "b", "a"])
    >>> wordlist
    WordList(['a', 'b', 'c'])
    >>> assert wordlist[0] == "a"
    >>> assert list(wordlist) == ["a", "b", "c"]
    >>> assert wordlist == WordList(["a", "b", "c"])
    """

    def __init__(
        self,
        words: Iterable[str] = [],
        *,
        min_word_size: int = 1,
        max_word_size: int | None = None,
    ):
        """Construct a wordlist from words.

        :param words: Words to construct wordlist from.
        :param min_word_size: Filter out words which are shorter than this.
        :param max_word_size: Filter out words which are longer than this. None means no
            filtering.
        """
        words = sorted(set(words))
        self._words: list[str] = words

        assert min_word_size > 0, "--min-word-size must be at least 1."
        assert (
            max_word_size is None or max_word_size >= min_word_size
        ), "--max-word-size must be greater or equal to --min-word-size"

        self._filter_min_word_size(min_word_size)
        self._filter_max_word_size(max_word_size)

    @overload
    def __getitem__(self, index: int) -> str: ...
    @overload
    def __getitem__(self, index: slice) -> "WordList": ...
    def __getitem__(self, index):
        if isinstance(index, int):
            return self._words[index]
        else:
            return WordList(self._words[index])

    def __len__(self) -> int:
        return len(self._words)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WordList):
            return False
        return self._words == other._words

    def __ne__(self, other: object) -> bool:
        return not self == other

    @overload
    def __add__(self, other: "WordList") -> "WordList": ...
    @overload
    def __add__(self, other: list) -> "WordList": ...
    def __add__(self, other) -> "WordList":
        if isinstance(other, WordList):
            return WordList(self._words + other._words)
        elif isinstance(other, list):
            return WordList(self._words + other)
        raise ValueError(f"Unsupported type {type(other)}")

    def __repr__(self) -> str:
        return f"{WordList.__name__}({self._words})"

    def to_file(self, file_path: Path | str) -> None:
        """Write this wordlist to a file (overwrites if file exists)."""
        with open(file_path, mode="w") as fout:
            fout.write("\n".join(self))

    @staticmethod
    def from_file(file_path: Path | str, **options):
        """Construct a wordlist from a file of words (newline separated).

        The options are the same as the kwargs for the __init__ function.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        assert file_path.exists(), f"Wordfile does not exist: {file_path}"

        with open(file_path, "r") as fin:
            words = [w.strip() for w in fin.readlines()]
            return WordList(words, **options)

    def _filter_min_word_size(self, min_word_size: int) -> None:
        self._words = [w for w in self._words if len(w) >= min_word_size]

    def _filter_max_word_size(self, max_word_size: int | None) -> None:
        if max_word_size is None:
            return

        self._words = [w for w in self._words if len(w) <= max_word_size]

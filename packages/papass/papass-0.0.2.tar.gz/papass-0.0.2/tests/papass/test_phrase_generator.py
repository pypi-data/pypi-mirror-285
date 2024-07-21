import pytest
from papass.phrase_generator import PhraseGenerator
from papass.wordlist import WordList

from tests.utils.cycle_rng import CycleRng


class TestPhraseGenerator:
    @pytest.fixture
    def wordlist(self):
        """Four words. Two bits of entropy per word."""
        return WordList(["a", "b", "c", "d"])

    @pytest.mark.parametrize(
        "cycle,phrase",
        [
            ([2], "cccc"),
            ([0, 1], "abab"),
            ([0, 3, 1, 2], "adbc"),
        ],
    )
    def test_get_phrase_uses_rng_choice_in_order(self, wordlist, cycle, phrase):
        rpg = PhraseGenerator(wordlist=wordlist, rng=CycleRng(cycle), delimiter="")

        assert rpg.get_phrase(4).phrase == phrase

    @pytest.mark.parametrize("count", range(4))
    def test_entropy(self, wordlist, count):
        rpg = PhraseGenerator(wordlist=wordlist, rng=CycleRng(range(4)), delimiter=" ")

        # wordlist has 4 words, so 2 bits of entropy per word.
        assert rpg.get_phrase(count).entropy == pytest.approx(2 * count)

    @pytest.mark.parametrize("delimiter", list(" @-*"))
    def test_delimiter(self, wordlist, delimiter: str):
        rpg = PhraseGenerator(
            wordlist=wordlist, rng=CycleRng(range(4)), delimiter=delimiter
        )

        assert rpg.get_phrase(3).phrase == delimiter.join(wordlist[:3])


class TestEntropyGuarantee:
    """We only test the following:

    - Guarantee MUST be True if current implementation SHOULD be able to prove it true.
    - Guarantee MUST be False if entropy IS indeed lower.

    For all other cases we do not test it because the implementation might become smarter.
    """

    @pytest.fixture
    def wordlist(self):
        """Wordlist with the following properties

        - Words do not contain `x` or `y`.
        - Using e.g. `a` as delimiter decreases the number of possible passphrases as compared to
          using ` `. For example `aaab` can occur in mulitple ways (from chosing `aa` and `b` as
          well as from chosing `a` and `ab`).
        """
        return WordList(["aa", "bb", "ab", "b", "a"])

    @pytest.mark.parametrize(
        "delimiter",
        [
            # If the delimiter is not from the alphabet of the words the entropy is guaranteed:
            " ",
            "#",
            "-",
            "x",
            "y",
        ],
    )
    def test_is_guaranteed(self, wordlist, delimiter):
        rpg = PhraseGenerator(
            wordlist=wordlist, delimiter=delimiter, rng=CycleRng([0, 1])
        )
        result = rpg.get_phrase(2)
        assert result.entropy_is_guaranteed

    @pytest.mark.parametrize(
        "delimiter",
        [
            "",
            "a",
            "b",
        ],
    )
    def test_is_not_guaranteed(self, wordlist, delimiter):
        """With the chosen wordlist these delimiters decrease the number of possible
        passphrases. Hence check must return False."""
        rpg = PhraseGenerator(
            wordlist=wordlist, delimiter=delimiter, rng=CycleRng([0, 1])
        )

        # Edge case: If only one word is generated the guarantee naturally holds.
        result_1 = rpg.get_phrase(1)
        result_2 = rpg.get_phrase(2)

        assert result_1.entropy_is_guaranteed
        assert not result_2.entropy_is_guaranteed

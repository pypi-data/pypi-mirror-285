import functools
from collections.abc import Callable
from dataclasses import asdict, dataclass
from itertools import chain
from typing import ParamSpec, TypeVar

import jiwer
import rapidfuzz
from misc_python_utils.beartypes import NeList, NeStr, nobeartype
from rapidfuzz.distance import Editop, Editops
from typing_extensions import Self

from speech_utils.asr_eval_utils.asr_metrics import (
    CharacterErrorRates,
    JiwerCharacterErrorRates,
)

rapidfuzz_distance_Levenshtein_editops = (  # noqa: N816
    rapidfuzz.distance.Levenshtein.editops
)


@dataclass
class CharacterErrorRatesOfInterest(CharacterErrorRates):
    @classmethod
    def parse(
        cls,
        refs: NeList[NeStr],
        hyps: NeList[str],
        chars_of_interest: set[str],
    ) -> Self:
        return cls(
            **character_error_rates_of_interest(refs, hyps, chars_of_interest),
        )


P = ParamSpec("P")
R = TypeVar("R")


def character_error_rates_of_interest(
    refs: NeList[str],
    hyps: NeList[str],
    chars_of_interest: set[str],
) -> dict[str, float]:
    patched = chars_of_interest_patch(JiwerCharacterErrorRates.parse, chars_of_interest)
    return asdict(patched(refs, hyps))


def chars_of_interest_patch(
    fun: Callable[P, R],
    chars_of_interest: set[str],
) -> Callable[P, R]:
    """
    patching: jiwer.process._word2char and rapidfuzz.distance.Levenshtein.editops
    to only consider characters of interest
    """

    @functools.wraps(fun)
    @nobeartype
    def patched(*args: P.args, **kwargs: P.kwargs) -> R:
        char2word = [{}]
        original_word2char = jiwer.process._word2char  # noqa: SLF001
        jiwer.process._word2char = build_word2char_patch(char2word)  # noqa: SLF001
        rapidfuzz.distance.Levenshtein.editops = editops_only_for_chars_of_interest(
            chars_of_interest=chars_of_interest,
            char2word=char2word,
        )
        rates = fun(*args, **kwargs)

        # revert the patch
        rapidfuzz.distance.Levenshtein.editops = rapidfuzz_distance_Levenshtein_editops
        jiwer.process._word2char = original_word2char  # noqa: SLF001
        return rates

    return patched


def build_word2char_patch(char2word: list[dict]) -> Callable:
    def _word2char_patched(  # noqa: ANN202
        reference: list[list[str]],
        hypothesis: list[list[str]],
    ):  # noqa: ANN202
        """
        returning list of lists of characters instead list of strings like in original,
         in order to "hack" this line:
            hits = len(reference_sentence) - (substitutions + deletions)
        in jiwer.process.process_words
        """
        # tokenize each word into an integer
        vocabulary = set(chain(*reference, *hypothesis))

        if "" in vocabulary:
            raise ValueError(  # noqa: TRY003
                "Empty strings cannot be a word. "  # noqa: EM101
                "Please ensure that the given transform removes empty strings.",
            )

        word2char = dict(zip(vocabulary, range(len(vocabulary)), strict=False))
        char2word[0] = {chr(v): k for k, v in word2char.items()}
        reference_chars = [
            [chr(word2char[w]) for w in sentence] for sentence in reference
        ]
        hypothesis_chars = [
            [chr(word2char[w]) for w in sentence] for sentence in hypothesis
        ]

        return reference_chars, hypothesis_chars

    return _word2char_patched


def editops_only_for_chars_of_interest(  # noqa: C901,WPS231
    chars_of_interest: set[str],
    char2word: list[dict],
) -> Callable[[list[str], list[str]], Editops]:
    def is_of_interest(char: str) -> bool:
        assert len(char) == 1
        recovered_char = char2word[0][char]
        return recovered_char in chars_of_interest

    def get_edit_op(ref_char: str, hyp_char: str) -> str:
        if is_of_interest(ref_char) and is_of_interest(hyp_char):
            return "replace" if ref_char != hyp_char else "insert"
        elif is_of_interest(ref_char):
            return "delete"
        else:
            return "insert"

    def patched_editops(ref_letters: list[str], hyp_letters: list[str]) -> Editops:
        ref = "".join(ref_letters)
        hyp = "".join(hyp_letters)
        editops = rapidfuzz_distance_Levenshtein_editops(ref, hyp)
        editops_of_interest = [
            Editop(
                tag=get_edit_op(ref[editop.src_pos], hyp[editop.dest_pos]),
                src_pos=editop.src_pos,
                dest_pos=editop.dest_pos,
            )
            for editop in editops
            if (
                is_of_interest(ref[editop.src_pos])
                and editop.tag in {"delete", "replace"}
            )
            or (
                is_of_interest(hyp[editop.dest_pos])
                and editop.tag in {"insert", "replace"}
            )
        ]
        for k in reversed(range(len(ref_letters))):
            if char2word[0][ref_letters[k]] not in chars_of_interest:
                ref_letters.pop(k)
            else:
                ref_letters[k] = (
                    "x"  # just to make sure that the ref_letters are not used in the final output
                )
        return Editops(editops_of_interest, len(ref), len(hyp))  # pyright: ignore [reportArgumentType]

    return patched_editops

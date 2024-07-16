from dataclasses import dataclass

import jiwer
import numpy as np
from misc_python_utils.beartypes import NeList, NeStr
from misc_python_utils.file_utils.readwrite_files import write_lines
from typing_extensions import Self


def calc_cer(refs: NeList[NeStr], hyps: NeList[str]) -> float:
    return character_error_rates(refs, hyps)["cer"]


def calc_wer(refs: NeList[NeStr], hyps: NeList[str]) -> float:
    return word_error_rates(refs, hyps)["wer"]


def micro_avg_asr_scores(
    refs_hyps: NeList[tuple[NeStr, str]],
) -> dict[str, dict[str, float]]:
    refs, hyps = (list(x) for x in zip(*refs_hyps, strict=True))
    return {
        "word": word_error_rates(refs, hyps),
        "char": character_error_rates(refs, hyps),
    }


def word_error_rates(refs: NeList[NeStr], hyps: NeList[str]) -> dict[str, float]:
    try:
        who = jiwer.process_words(refs, hyps)
    except ValueError as e:
        write_lines("refs.txt", refs)
        raise e  # noqa: TRY201 TODO: jiwer's text-processing might fail, jiwer's fault to not have separated concerns!
    num_words = sum(len(r) for r in who.references)
    assert num_words == who.hits + who.deletions + who.substitutions
    return {
        "wer": who.wer,
        "insr": who.insertions / num_words,
        "delr": who.deletions / num_words,
        "subr": who.substitutions / num_words,
        # "hit": who.hits / num_words,
    }


@dataclass
class CharacterErrorRates:
    cer: float
    insr: float
    delr: float
    subr: float
    hitr: float  # ,recall,TPR
    # support: int # is not an error -rate!


@dataclass
class JiwerCharacterErrorRates(CharacterErrorRates):
    @classmethod
    def parse(cls, refs: NeList[NeStr], hyps: NeList[str]) -> Self:
        return cls(**character_error_rates(refs, hyps))


def character_error_rates(refs: NeList[str], hyps: NeList[str]) -> dict[str, float]:
    cho = jiwer.process_characters(refs, hyps)  # might "remove"/filter letters
    num_all_chars = sum(len(r) for r in cho.references)
    num_chars_of_interest = (
        cho.hits + cho.deletions + cho.substitutions
    )  # this is "normally" the same as the above line, except if one patches the editops to account only for words of interest
    assert (
        num_chars_of_interest <= num_all_chars
    )  # process_characters might remove/filter letters

    return {
        "cer": cho.cer,
        "insr": cho.insertions / num_chars_of_interest,
        "delr": cho.deletions / num_chars_of_interest,
        "subr": cho.substitutions / num_chars_of_interest,
        "hitr": cho.hits / num_chars_of_interest,
        # "support": num_chars
    }


def percentile_stats(
    data: list[float],
    percentiles: list[int] | None = None,
) -> dict[str, float | int]:
    if percentiles is None:
        percentiles = [25, 50, 75, 95]
    stats: dict[str, int | float] = {
        f"p{p}": float(np.percentile(data, q=p)) for p in percentiles
    }
    stats["max"] = max(data)
    stats["min"] = min(data)
    stats["num"] = len(data)
    return stats

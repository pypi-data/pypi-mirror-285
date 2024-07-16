import typing
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Protocol

from buildable_dataclasses.buildable import Buildable
from misc_python_utils.slugification import CasedNameSlug

from speech_utils.asr_eval_utils.pretty_diff import smithwaterman_aligned_icdiff
from speech_utils.data_models.timespans_with_text import IdText


@dataclass(slots=True)
class IcDiffSample:
    diff_title: str
    ansi_diff: str


@dataclass
class DiffTitle:
    def get_title(self, ref: IdText, hyp: IdText) -> str:  # noqa: ARG002, PLR6301
        return f"\n{ref.sample_id}"


@typing.runtime_checkable
class IdTextCorpusP(Iterable[IdText], Protocol):
    name: CasedNameSlug


@dataclass
class AnsiIcDiffs(Buildable, Iterable[IcDiffSample]):
    ref: IdTextCorpusP
    hyp: IdTextCorpusP
    diff_title: DiffTitle = field(default_factory=DiffTitle)

    def __iter__(self) -> Iterator[IcDiffSample]:
        yield from (
            IcDiffSample(
                diff_title=self.diff_title.get_title(ref, hyp),
                ansi_diff=smithwaterman_aligned_icdiff(
                    ref.text,
                    hyp.text,
                    ref_header=self.ref.name,
                    hyp_header=self.hyp.name,
                )
                if len(ref.text) > 0 and len(hyp.text) > 0
                else f"no diff possible for ref: {ref.text}\thyp: {hyp.text}",
            )
            for ref, hyp in zip(
                self.ref,
                self.hyp,
                strict=True,
            )  # TODO: it threw an error for having different sequence lenghts in the zip -> check transcript files!
            # desc=f"{self.__class__.__name__},{self.cleaned_ref_hyp.ref.name},{self.cleaned_ref_hyp.hyp.name}",
            # )
        )

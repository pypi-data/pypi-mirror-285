from dataclasses import dataclass
from typing import TypeVar

from misc_python_utils.beartypes import NeSequence

from speech_utils.audio_segmentation_utils.non_overlapping_segments import (
    NeNoSegments,
    NonOverlapTimeSpans,
)
from speech_utils.data_models.audio_array_models import (
    NeMsTimeSpanAudioArray,
    NeMsTimeSpanTextAudioArray,
)
from speech_utils.data_models.timespans_with_text import (
    MsTimeSpanNeText,
    MsTimeSpanText,
    NeMsTimeSpanNeText,
    NeTimeSpanNeText,
    TimeSpanText,
)


@dataclass
class TextNeNoSeg(
    NeNoSegments[TimeSpanText],
):  # not using a protocol here to be stricter with data-validation?
    segments: NeSequence[TimeSpanText]

    @property
    def text(self) -> str:
        return "".join([seg.text for seg in self.segments])


TTextNeNoSeg = TypeVar("TTextNeNoSeg", bound=TextNeNoSeg)


@dataclass
class MsTimeSpanTextNeNoSeq(TextNeNoSeg[MsTimeSpanText]):
    segments: NeSequence[MsTimeSpanText]  # necessary to trigger beartypes type checking


@dataclass
class MsTimeSpanNeTextNeNoSeg(TextNeNoSeg[MsTimeSpanNeText]):
    """
    time-spans might have zero duration!
    """

    segments: NeSequence[MsTimeSpanNeText]


@dataclass
class NeSpanNeTextNeNoSegs(TextNeNoSeg[NeTimeSpanNeText]):
    segments: NeSequence[
        NeTimeSpanNeText
    ]  # necessary to trigger beartypes type checking


NeTimeSpanTextNonOverlap = NeSpanNeTextNeNoSegs


@dataclass
class NeMsTimeSpanNeTextNeNoSeg(TextNeNoSeg[NeMsTimeSpanNeText]):
    segments: NeSequence[
        NeMsTimeSpanNeText
    ]  # necessary to trigger beartypes type checking


NeMsTimeSpanTextNonOverlap = NeMsTimeSpanNeTextNeNoSeg


@dataclass
class NonOverlapNeMsTimeSpanAudioArrays(NonOverlapTimeSpans[NeMsTimeSpanAudioArray]):
    segments: NeSequence[
        NeMsTimeSpanAudioArray
    ]  # necessary to trigger beartypes type checking


@dataclass
class NonOverlapNeMsTimeSpanTextsAudioArrays(
    TextNeNoSeg[NeMsTimeSpanTextAudioArray],
):
    segments: NeSequence[
        NeMsTimeSpanTextAudioArray
    ]  # necessary to trigger beartypes type checking

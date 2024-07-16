from dataclasses import dataclass
from typing import Generic

from misc_python_utils.utils import Singleton
from typing_extensions import Self

from speech_utils.audio_segmentation_utils.non_overlapping_segments_variations import (
    TextNeNoSeg,
)
from speech_utils.data_models.misc_data_types import EmptySeq
from speech_utils.data_models.timespans_with_text import TTimeSpanTextP


@dataclass
class StreamingASRMessage(Generic[TTimeSpanTextP]):
    """
    formerly called ASRMessage
    """

    id_: str
    segments: (
        TextNeNoSeg[TTimeSpanTextP] | EmptySeq[TTimeSpanTextP]
    )  # more explicit non-empty or None
    # end_of_message: bool = False # removed end_of_message cause it was only carrying/handing through the EOS signal

    @classmethod
    def cut_append(cls, first: Self, second: Self) -> Self:
        first_segments = first.segments
        if not isinstance(first_segments, EmptySeq) and not isinstance(
            second.segments,
            EmptySeq,
        ):
            segments = first_segments.cut_append(second.segments)

        elif isinstance(second.segments, EmptySeq):
            segments = first_segments
        else:
            segments = second.segments

        return cls(
            id_=first.id_,
            segments=segments,
        )


Seconds = float


@dataclass
class EndOfAudioStream(metaclass=Singleton):  # noqa: N801
    pass


END_OF_AUDIO_STREAM = EndOfAudioStream()

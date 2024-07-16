import logging
import os
from typing import Annotated

import soundfile
from beartype.vale import Is
from misc_python_utils.beartypes import NeNpFloatDim1

from speech_utils.audio_segmentation_utils._overengineered_segment_merging import (
    MergedCloseAndShortOrOverlappingSegmentsParser,
)
from speech_utils.audio_segmentation_utils.non_overlapping_segments import NeNoSegments
from speech_utils.audio_segmentation_utils.ordered_spans import (
    OrderedOverlappingSpans,
    OrderedSpans,
)
from speech_utils.audio_segmentation_utils.ordered_time_stamps import OrderedTimeStamps
from speech_utils.data_models.time_spans import TimeSpan, TTimeSpanP

logger = logging.getLogger(__name__)


SOME_BIG_VALUE = 12.3


PositiveFloat = Annotated[float, lambda x: x > 0]


def segment_letter_timestamps(
    timestamps: OrderedTimeStamps,
    end: PositiveFloat,
    min_seg_dur: float = 1.5,
    max_gap_dur: float = 0.2,
    expand_by: float = 0.1,
) -> NeNoSegments[TimeSpan]:
    letter_duration = (
        0.04  # heuristic -> 40ms is median of some transcript, sounds plausible!
    )
    segments = OrderedSpans[TimeSpan].create_dont_validate(
        [TimeSpan(start=ts, end=min(ts + letter_duration, end)) for ts in timestamps],
    )
    segments = expand_segments(segments, end=end, expand_by=expand_by)
    merged_segments = MergedCloseAndShortOrOverlappingSegmentsParser(
        max_gap_dur=max_gap_dur,
        min_seg_dur=min_seg_dur,
    ).parse(segments)
    return MergedCloseAndShortOrOverlappingSegmentsParser(
        max_gap_dur=3.0,
        min_seg_dur=min_seg_dur,
    ).parse(
        merged_segments,
    )


# def expand_merge_segments(
#     segments: OrderedSpans[TTimeSpanP],
#     end: PositiveFloat,
#     expand_by: Annotated[float, Is[lambda x: x > 0]] = 0.1,
#     min_gap_dur: float = 0.2,
# ) -> NeNoSegments[TTimeSpanP]:
#     """
#     TODO: remove this!
#     """
#     return NeNoSegments.merge_close_segments(
#         expand_segments(segments, end=end, expand_by=expand_by),
#         min_gap_dur,
#     )


def expand_segments(
    segments: OrderedSpans[TTimeSpanP],
    end: PositiveFloat,
    expand_by: Annotated[float, Is[lambda x: x > 0]] = 0.1,
) -> NeNoSegments[TTimeSpanP]:
    raw_expanded = OrderedSpans.create_dont_validate(  # TODO: instantiation does "validate" which might be redundant!
        [
            type(seg)(
                **(
                    seg.to_dict()
                    | {
                        "start": max(seg.start - expand_by, 0.0),
                        "end": min(seg.end + expand_by, end),
                    }
                ),
            )
            for seg in segments
        ],
    )
    overlapping = OrderedOverlappingSpans.parse(raw_expanded)
    return NeNoSegments.parse(overlapping)


# def merge_short_segments(
#     segments: NeNoSegments[TimeSpan],
#     min_dur: float = 1.5,
# ) -> NeNoSegments[TimeSpan]:
#     """
#     should be the same as
#     MergedCloseSegmentsParser(
#         max_gap_dur=None,
#         min_seg_dur=min_seg_dur,
#     ).parse(merged_segments)
#     """
#     GIVE_ME_NEW_START = -1.111
#
#     def buffer_segment(segs: NeNoSegments[TimeSpan]) -> Iterator[TimeSpan]:
#         previous_start: float = GIVE_ME_NEW_START
#         for seg in segs:
#             if previous_start == GIVE_ME_NEW_START:
#                 previous_start = seg.start
#
#             if seg.end - previous_start > min_dur:
#                 yield TimeSpan(previous_start, seg.end)
#                 previous_start = GIVE_ME_NEW_START
#
#         if previous_start != GIVE_ME_NEW_START:
#             yield TimeSpan(
#                 previous_start,
#                 seg.end,
#             )
#
#     min_dur_segs = list(buffer_segment(segments))
#     last = min_dur_segs[-1]
#     do_merge_the_last_with_the_previous = (
#         last.end - last.start < min_dur and len(min_dur_segs) > 1
#     )
#     if do_merge_the_last_with_the_previous:
#         last = min_dur_segs.pop(-1)
#         previous = min_dur_segs[-1]
#         min_dur_segs[-1] = TimeSpan(previous.start, last.end)
#
#     return NeNoSegments(min_dur_segs)


def write_segmentwise_wav_file_just_for_fun(
    start_end_speaker: list[tuple[float, float, str]],
    array: NeNpFloatDim1,
    SR: int = 16000,
) -> None:
    output_dir = "segments_wavs"
    os.makedirs(output_dir, exist_ok=True)  # noqa: PTH103
    for k, (s, e, sp) in enumerate(start_end_speaker):
        soundfile.write(
            f"{output_dir}/{k}_{sp}.wav",
            array[round(s * SR) : round(e * SR)],
            samplerate=SR,
        )

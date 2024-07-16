from dataclasses import dataclass
from typing import Generic, TypeVar

from speech_utils.audio_segmentation_utils.already_validated_input_data import (
    AlreadyValidatedInputData,
    DontParseUseParser,
)
from speech_utils.audio_segmentation_utils.merged_close_segments import (
    merge_close_and_short_or_overlapping_segments,
)
from speech_utils.audio_segmentation_utils.non_overlapping_segments import NeNoSegments
from speech_utils.audio_segmentation_utils.ordered_spans import OrderedSpans
from speech_utils.data_models.time_spans import TimeSpan

TTimeSpan_co = TypeVar("TTimeSpan_co", bound=TimeSpan, covariant=True)
# TODO: MergedCloseAndShortOrOverlappingSegmentsParser is overengineering! -> just use a function!


@dataclass(kw_only=True)
class MergedCloseAndShortOrOverlappingSegments(
    AlreadyValidatedInputData,
    DontParseUseParser,
    NeNoSegments[TTimeSpan_co],  # HasNeNoSeg[TTimespan_co]
):
    """
    this class is an example of a hybrid/trade-off between type-driven (parse) and "conventional" ([data-]validating) development-style
    it does carry some information in the type and some as fields in the instance
    _factory field only to "enforce" that the factory is used to create instances
    """

    max_gap_dur: float
    min_seg_dur: float | None = None


@dataclass
class MergedCloseAndShortOrOverlappingSegmentsParser(Generic[TTimeSpan_co]):
    """
    acts like a factory for MergedCloseSegments
    separates parameterization from the actual parsing input-data
    """

    # gap within between two segments -> shorter than this gets merged
    max_gap_dur: float = 0.2
    # close segments only get merged if at least one is shorter than this
    min_seg_dur: float | None = None

    def parse(
        self,
        segments: NeNoSegments[
            TTimeSpan_co
        ]  # TODO: would be cool to have TNeNoSegments[TTimeSpan_co] here, but not possible in python
        | OrderedSpans[
            TTimeSpan_co
        ],  # no higher-level type-vars so no way to indicate things like this: TextNeNoSeg[TTimeSpanText_co]
    ) -> MergedCloseAndShortOrOverlappingSegments[TTimeSpan_co]:
        merged_segments = merge_close_and_short_or_overlapping_segments(
            segments,
            self.max_gap_dur,
            self.min_seg_dur,
        )
        return MergedCloseAndShortOrOverlappingSegments(
            _input_data_is_already_validated=True,
            segments=merged_segments.segments,
            max_gap_dur=self.max_gap_dur,
            min_seg_dur=self.min_seg_dur,
        )

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic

from misc_python_utils.slugification import CasedNameSlug

from speech_utils.audio_segmentation_utils.non_overlapping_segments_variations import (
    TextNeNoSeg,
)
from speech_utils.data_models.audio_array_models import AudioArray
from speech_utils.data_models.enter_exit_service import EnterExitService
from speech_utils.data_models.misc_data_types import EmptySeq
from speech_utils.data_models.timespans_with_text import TTimeSpanTextP

logger = logging.getLogger(__name__)


@dataclass
class AudioArray2SegmentedTranscripts(EnterExitService, ABC, Generic[TTimeSpanTextP]):
    name: CasedNameSlug

    @abstractmethod
    def audio_to_segmented_transcripts(
        self,
        audio_array: AudioArray,
    ) -> TextNeNoSeg[TTimeSpanTextP] | EmptySeq[TTimeSpanTextP]:
        # TODO: still too "loose" of a return type
        # TODO: Result[TextNeNoSeg, str]
        ...

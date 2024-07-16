from abc import abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass

from misc_python_utils.beartypes import NeList
from misc_python_utils.slugification import CasedNameSlug

from speech_utils.asr_utils.accumulating_asr_streamer import _accumulate_message
from speech_utils.asr_utils.streaming_asr_utils import StreamingASRMessage
from speech_utils.audio_segmentation_utils.non_overlapping_segments_variations import (
    TextNeNoSeg,
)
from speech_utils.data_models.misc_data_types import EmptySeq
from speech_utils.signal_chunking.audio_signal_chunk import AudioSignalChunk


@dataclass(kw_only=True)
class AccumulatingLongformASRInferencer(AbstractContextManager):
    name: CasedNameSlug

    @property
    @abstractmethod
    def input_sample_rate(self) -> int: ...

    def longform_infer_cumulative(
        self,
        audio_chunks: NeList[AudioSignalChunk],
    ) -> TextNeNoSeg | EmptySeq:
        messages = self._longform_infer(audio_chunks)
        cumulative_message = None
        for msg in messages:
            cumulative_message = _accumulate_message(
                msg,
                cumulative_message,
                max_dur=365 * 24 * 60 * 60 + 0.123,
            )
        self._reset_streamer()
        assert isinstance(
            cumulative_message,
            StreamingASRMessage,
        )  # type narrowing to help pyright
        return cumulative_message.segments

    @abstractmethod
    def _longform_infer(
        self,
        audio_chunks: NeList[AudioSignalChunk],
    ) -> NeList[StreamingASRMessage]:
        """
        to be implemented but not called directly
        """
        ...

    def _reset_streamer(
        self,
    ) -> None:
        """
        just to show that there is a reset, but is not supposed to be called directly but instead is triggered by END_OF_AUDIO_STREAM signal
        """
        self.cumulative_message = None

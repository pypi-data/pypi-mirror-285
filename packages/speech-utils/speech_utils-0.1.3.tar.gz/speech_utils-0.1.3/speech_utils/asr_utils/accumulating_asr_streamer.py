from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic

from misc_python_utils.slugification import CasedNameSlug

from speech_utils.asr_utils.streaming_asr_utils import (
    END_OF_AUDIO_STREAM,
    EndOfAudioStream,
    Seconds,
    StreamingASRMessage,
)
from speech_utils.data_models.enter_exit_service import EnterExitService
from speech_utils.data_models.misc_data_types import EmptySeq
from speech_utils.data_models.timespans_with_text import TTimeSpanTextP
from speech_utils.signal_chunking.audio_signal_chunk import AudioSignalChunk


@dataclass(kw_only=True)
class AccumulatingASRStreamInferencer(EnterExitService, ABC, Generic[TTimeSpanTextP]):
    """

    ░▀▄░░▄▀
    ▄▄▄██▄▄▄▄▄
    █▒░▒░▒░█▀█
    █░▒░▒░▒█▀█
    █▄▄▄▄▄▄███

    """

    name: CasedNameSlug
    cumulative_message: StreamingASRMessage[TTimeSpanTextP] | None = None
    max_accum_size: Seconds = 3600.0
    input_sample_rate: int = 16000

    def stream_infer_cumulative(
        self,
        audio_chunk: AudioSignalChunk | EndOfAudioStream,
    ) -> Iterator[StreamingASRMessage[TTimeSpanTextP]]:
        for msg in self._stream_infer(audio_chunk):
            self.cumulative_message = _accumulate_message(
                msg,
                self.cumulative_message,
                self.max_accum_size,
            )
            yield self.cumulative_message
        if audio_chunk is END_OF_AUDIO_STREAM:
            self._reset_streamer()

    @abstractmethod
    def _stream_infer(
        self,
        audio_chunk: AudioSignalChunk | EndOfAudioStream,
    ) -> Iterator[StreamingASRMessage[TTimeSpanTextP]]:
        """
        to be implemented but not called directly
        """
        ...

    def _enter_service(self) -> None:
        self._enter_streaming_service()

    def _exit_service(self) -> None:
        self._exit_streaming_service()

    def _reset_streamer(
        self,
    ) -> None:
        """
        just to show that there is a reset, but is not supposed to be called directly but instead is triggered by END_OF_AUDIO_STREAM signal
        """
        self.cumulative_message = None

    def _enter_streaming_service(self) -> None:
        pass

    def _exit_streaming_service(self) -> None:
        pass


def _accumulate_message(
    msg: StreamingASRMessage[TTimeSpanTextP],
    cum_msg: StreamingASRMessage[TTimeSpanTextP] | None,
    max_dur: Seconds,
) -> StreamingASRMessage[TTimeSpanTextP]:
    cum_msg = (
        cum_msg.cut_append(cum_msg, msg)
        if isinstance(cum_msg, StreamingASRMessage)
        else msg
    )
    segments = cum_msg.segments
    return (
        StreamingASRMessage(
            id_=cum_msg.id_,
            segments=segments.create_without_validation(
                segments.slice_segments(
                    start=max(segments[-1].end - max_dur, 0.0),
                ),
            ),
        )
        if not isinstance(segments, EmptySeq)
        else cum_msg
    )

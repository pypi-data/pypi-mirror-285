import logging
from dataclasses import dataclass, field

from speech_utils.data_models.time_spans import Seconds
from speech_utils.signal_chunking.audio_signal_chunk import AudioSignalChunk
from speech_utils.signal_chunking.fixed_size_chunker import FixedSizeChunker
from speech_utils.signal_chunking.increasing_size_chunker import (
    _DONT_EMIT_PREMATURE_CHUNKS,
    DONT_EMIT_PREMATURE_CHUNKS,
)
from speech_utils.signal_chunking.initially_increasing_then_fixed_size_chunking import (
    InitiallyIncreasingThenFixedChunker,
)

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class FixedSizeAudioChunker(FixedSizeChunker):
    chunk_dur: Seconds
    min_step_dur: (
        Seconds  # if step_size==chunk_size it produced non-overlapping segments
    )
    max_step_dur: Seconds | None = None
    sample_rate: int = field(init=False, repr=False)

    chunk_size: int = field(init=False)
    min_step_size: int = field(
        init=False,
        repr=False,
    )  # if step_size==chunk_size it produced non-overlapping segments
    max_step_size: int | None = field(init=False, default=None)

    def set_sample_rate(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate
        self.chunk_size = int(self.chunk_dur * sample_rate)
        self.min_step_size = int(self.min_step_dur * sample_rate)
        if self.max_step_dur is not None:
            self.max_step_size = int(self.max_step_dur * sample_rate)


@dataclass
class AudioChunker(InitiallyIncreasingThenFixedChunker[AudioSignalChunk]):
    fxd_chkr: FixedSizeAudioChunker
    #  TODO: https://fossies.org/linux/pyright/docs/type-concepts-advanced.md
    sample_rate: int = 16_000
    minimum_chunk_dur: Seconds | _DONT_EMIT_PREMATURE_CHUNKS = (
        DONT_EMIT_PREMATURE_CHUNKS
    )
    minimum_chunk_size: int | _DONT_EMIT_PREMATURE_CHUNKS = field(
        init=False,
        default=DONT_EMIT_PREMATURE_CHUNKS,
    )

    def __post_init__(self):
        self._set_sample_rate(self.sample_rate)

    def buffer_and_chunk(self, inpt_msg: AudioSignalChunk) -> list[AudioSignalChunk]:
        if self.sample_rate != inpt_msg.sample_rate:
            self._set_sample_rate(inpt_msg.sample_rate)
        return super().buffer_and_chunk(inpt_msg)

    def _set_sample_rate(self, sample_rate: int) -> None:
        self.fxd_chkr.set_sample_rate(sample_rate)
        if not isinstance(self.minimum_chunk_dur, _DONT_EMIT_PREMATURE_CHUNKS):
            self.minimum_chunk_size = int(
                self.minimum_chunk_dur * self.fxd_chkr.sample_rate,
            )
            self._incr_chkr = self._build_incr_chkr()

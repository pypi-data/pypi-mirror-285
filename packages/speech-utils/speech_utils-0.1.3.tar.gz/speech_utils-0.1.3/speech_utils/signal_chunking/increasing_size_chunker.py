import logging
from dataclasses import dataclass, field

from misc_python_utils.utils import Singleton

from speech_utils.signal_chunking.signal_chunker import (
    ArrayBufferingSignalChunker,
    TChunkable,
    update_buffer,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _DONT_EMIT_PREMATURE_CHUNKS(metaclass=Singleton):  # noqa: N801
    pass


DONT_EMIT_PREMATURE_CHUNKS = _DONT_EMIT_PREMATURE_CHUNKS()


@dataclass(kw_only=True)
class IncreasingSizeChunker(ArrayBufferingSignalChunker[TChunkable]):
    minimum_chunk_size: int
    min_step_size: int

    _buffer: TChunkable | None = field(init=False, default=None)
    _last_buffer_size: int = field(
        init=False,
        repr=False,
        default=0,
    )

    def reset_chunker(self) -> None:
        self._last_buffer_size = 0
        self._buffer = None

    def _flush_chunker(self) -> list[TChunkable]:
        return [self._buffer] if self._buffer is not None else []

    def buffer_and_chunk(self, inpt_msg: TChunkable) -> list[TChunkable]:
        self._buffer = update_buffer(self._buffer, inpt_msg)
        if (emittable_chunk := self._get_emittable_chunk(self._buffer)) is not None:
            self._last_buffer_size = len(emittable_chunk)
            outp_msgs = [emittable_chunk]
        else:
            outp_msgs = []
        return outp_msgs

    def _get_emittable_chunk(self, buffer: TChunkable | None) -> TChunkable | None:
        buffer_size = len(buffer) if buffer is not None else 0
        premature_chunk_long_enough_to_yield_again = (
            buffer_size >= self._last_buffer_size + self.min_step_size
        )
        can_emit_premature_chunk = (
            self.minimum_chunk_size is not DONT_EMIT_PREMATURE_CHUNKS
            and buffer_size >= self.minimum_chunk_size
            and premature_chunk_long_enough_to_yield_again
        )
        return buffer if can_emit_premature_chunk else None

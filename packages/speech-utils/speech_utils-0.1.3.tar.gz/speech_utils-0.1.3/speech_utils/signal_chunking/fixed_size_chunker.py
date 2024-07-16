import logging
from dataclasses import dataclass, field
from typing import TypeVar

from speech_utils.signal_chunking.signal_chunker import (
    ArrayBufferingSignalChunker,
    TChunkable,
    update_buffer,
)

logger = logging.getLogger(__name__)
IS_VERY_START = -1


@dataclass(kw_only=True)
class FixedSizeChunker(ArrayBufferingSignalChunker[TChunkable]):
    """
    fixed size but adaptive step-size!
    """

    chunk_size: int
    min_step_size: int  # if step_size==chunk_size it produced non-overlapping segments
    max_step_size: int | None = None

    _buffer: TChunkable | None = field(init=False, default=None)
    _frame_counter: int = IS_VERY_START

    def reset_chunker(self) -> None:
        self._buffer = None
        self._frame_counter = IS_VERY_START

    def buffer_and_chunk(self, inpt_msg: TChunkable) -> list[TChunkable]:
        self._buffer = update_buffer(self._buffer, inpt_msg)
        msg_chunks: list[TChunkable] = []
        while (
            chunkable_buffer := self._get_chunkable_buffer(
                buffer=self._buffer,
                min_step_size=0 if self.is_very_start else self.min_step_size,
            )
        ) is not None:
            step_size = self._calc_next_step_size(len(chunkable_buffer))
            self._buffer = chunkable_buffer.slice_chunk(
                chunk=chunkable_buffer,
                start=step_size,
            )
            self._frame_counter = (
                self._frame_counter + step_size if not self.is_very_start else step_size
            )

            chunk = self._buffer.slice_chunk(
                chunk=self._buffer,
                end=self.chunk_size,
            )
            msg_chunks.append(chunk)
        return msg_chunks

    def _calc_next_step_size(self, buffer_size: int) -> int:
        if self.max_step_size is None:
            sz = self.min_step_size
        else:
            buffer_grew_by = buffer_size - self.chunk_size
            sz = _lower_upper_limit(
                buffer_grew_by,
                self.min_step_size,
                self.max_step_size,
            )
        return 0 if self.is_very_start else sz

    def _get_chunkable_buffer(
        self,
        buffer: TChunkable | None,
        min_step_size: int,
    ) -> TChunkable | None:
        buffer_size = len(buffer) if buffer is not None else 0
        if buffer_size >= self.chunk_size + min_step_size:
            return buffer
        else:
            return None

    def _flush_chunker(self) -> list[TChunkable]:
        self._frame_counter = IS_VERY_START
        one = 1
        flushable_chunk = self._get_chunkable_buffer(
            self._buffer,
            min_step_size=one,
        )
        out: list[TChunkable]
        if flushable_chunk is not None:
            chsz = self.chunk_size
            bfsz = len(self._buffer) if self._buffer is not None else 0
            assert (
                bfsz <= chsz + self.min_step_size
            ), f"cannot happen that len of buffer: {bfsz} > { chsz=}"

            non_overlapping = self.chunk_size == self.min_step_size
            if non_overlapping:  # noqa: SIM108
                start = self.chunk_size
            else:
                start = len(flushable_chunk) - chsz
            out = [
                flushable_chunk.slice_chunk(
                    chunk=flushable_chunk,
                    start=start,
                ),
            ]

        else:
            out = []
        return out

    @property
    def is_very_start(self) -> bool:
        return self._frame_counter == IS_VERY_START


IntFloat = TypeVar("IntFloat", int, float)


def _lower_upper_limit(x: IntFloat, lower: IntFloat, upper: IntFloat) -> IntFloat:
    return max(min(x, upper), lower)


"""

    def _calc_output_chunks(
        self,
        buffer: TChunkable | None,
    ) -> NewBufferAndChunks:
        chunks: list[TChunkable] = []
        while (
            chunkable_buffer := self._get_chunkable_buffer(
                buffer=buffer,
                min_step_size=0 if self.is_very_start else self.min_step_size,
            )
        ) is not None:
            step_size = self._calc_next_step_size()
            buffer = chunkable_buffer.slice_chunk(
                chunk=chunkable_buffer,
                start=step_size,
            )
            self._frame_counter = (
                self._frame_counter + step_size if not self.is_very_start else step_size
            )

            chunk = buffer.slice_chunk(
                chunk=buffer,
                end=self.chunk_size,
            )
            chunks.append(chunk)
        return NewBufferAndChunks(
            new_buffer=buffer,
            chunks=chunks,
        )

"""

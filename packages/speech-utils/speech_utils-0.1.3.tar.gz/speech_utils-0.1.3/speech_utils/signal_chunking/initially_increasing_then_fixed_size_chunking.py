import logging
from dataclasses import dataclass, field

from speech_utils.signal_chunking.fixed_size_chunker import FixedSizeChunker
from speech_utils.signal_chunking.increasing_size_chunker import (
    _DONT_EMIT_PREMATURE_CHUNKS,
    DONT_EMIT_PREMATURE_CHUNKS,
    IncreasingSizeChunker,
)
from speech_utils.signal_chunking.signal_chunker import (
    ArrayBufferingSignalChunker,
    TChunkable,
)

logger = logging.getLogger(__name__)


@dataclass
class InitiallyIncreasingThenFixedChunker(ArrayBufferingSignalChunker[TChunkable]):
    """
    formerly called OverlapArrayChunker
    after internal buffer grew bigger than chunk_size, it behaves as ring-buffer and further output_chunks all have chunk_size
    """

    fxd_chkr: FixedSizeChunker[TChunkable]
    minimum_chunk_size: int | _DONT_EMIT_PREMATURE_CHUNKS = DONT_EMIT_PREMATURE_CHUNKS
    _incr_chkr: IncreasingSizeChunker[TChunkable] | None = field(
        init=False,
        repr=False,
        default=None,
    )
    _fullgrown_mode: bool = field(
        init=False,
        repr=False,
        default=False,
    )

    def __post_init__(self):
        self._incr_chkr = self._build_incr_chkr()

    def _build_incr_chkr(self) -> IncreasingSizeChunker[TChunkable] | None:
        if not isinstance(self.minimum_chunk_size, _DONT_EMIT_PREMATURE_CHUNKS):
            _incr_chkr = IncreasingSizeChunker[TChunkable](
                minimum_chunk_size=self.minimum_chunk_size,
                min_step_size=self.fxd_chkr.min_step_size,
            )
            # _ = self._incr_chkr.flush_reset_chunker()
        else:
            _incr_chkr = None
        return _incr_chkr

    def reset_chunker(self) -> None:
        self._fullgrown_mode = False
        self.fxd_chkr.reset_chunker()
        if self._incr_chkr is not None:
            self._incr_chkr.reset_chunker()

    def buffer_and_chunk(self, inpt_msg: TChunkable) -> list[TChunkable]:
        fullgrown = self.fxd_chkr.buffer_and_chunk(inpt_msg)
        if len(fullgrown) > 0:
            self._fullgrown_mode = True
            if self._incr_chkr is not None:
                self._incr_chkr.flush_reset_chunker()
        if self._fullgrown_mode:
            out = fullgrown
        elif self._incr_chkr is not None:
            out = self._incr_chkr.buffer_and_chunk(inpt_msg)
        else:
            out = []
        return out

    def _flush_chunker(self) -> list[TChunkable]:
        if self._fullgrown_mode:
            out = self.fxd_chkr.flush_reset_chunker()
        elif self._incr_chkr is not None:  # bug found by mypy
            out = self._incr_chkr.flush_reset_chunker()
        else:
            out = []
        return out

import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Annotated, Generic, TypeVar

import numpy as np
from beartype.vale import Is
from misc_python_utils.beartypes import NpNumber
from misc_python_utils.utils import Singleton
from numpy.typing import NDArray
from typing_extensions import Self

PositiveInt = Annotated[int, Is[lambda x: x >= 0]]


@dataclass
class Chunkable(ABC):
    def append_chunk(self, other: Self) -> Self:
        return self.concat_chunks(self, other)

    @classmethod
    @abstractmethod
    def concat_chunks(
        cls,
        a: Self,
        b: Self,
    ) -> Self: ...

    @classmethod
    @abstractmethod
    def slice_chunk(
        cls,
        chunk: Self,
        start: PositiveInt | None = None,
        end: PositiveInt | None = None,
    ) -> Self: ...

    @abstractmethod
    def __len__(self) -> int: ...


@dataclass
class FlushAndResetChunker(metaclass=Singleton):  # noqa: N801
    pass


FLUSH_AND_RESET_CHUNKER = FlushAndResetChunker()

TNumpyArrayNumber = TypeVar("TNumpyArrayNumber", bound=NDArray[NpNumber])


@dataclass(kw_only=True)
class SignalChunk(Chunkable, Generic[TNumpyArrayNumber]):
    """
    formerly called MessageChunk
    """

    signal_id: str  # same for all chunks of same message
    frame_idx: Annotated[
        int,
        Is[lambda x: x >= 0],
    ]  # points to very first frame of this chunk
    array: TNumpyArrayNumber  # might be empty! -> TODO: make this more explicit?

    @classmethod
    def concat_chunks(
        cls,
        a: Self,
        b: Self,
    ) -> Self:
        # old name: concat_message
        assert a.signal_id == b.signal_id, f"{a.signal_id=}!={b.signal_id=}"
        frame_idx_consistency = a.frame_idx + len(a.array) == b.frame_idx
        assert frame_idx_consistency, f"to be concatenated chunks must not have gaps nor overlap {a.frame_idx + len(a.array)=}!={b.frame_idx}"
        array = np.concatenate([a.array, b.array], axis=0)
        return dataclasses.replace(a, array=array)

    @classmethod
    def slice_chunk(
        cls,
        chunk: Self,
        start: PositiveInt | None = None,
        end: PositiveInt | None = None,
    ) -> Self:
        """
        start, end are relative!
        """
        start_: PositiveInt = 0 if start is None else start
        end_: PositiveInt = len(chunk) if end is None else end
        return dataclasses.replace(
            chunk,
            array=chunk.array[start_:end_],
            frame_idx=chunk.frame_idx + start_,
        )

    def __len__(self) -> int:
        return self.array.shape[0]


def signal_chunks_from_arrays(
    signal_id: str,
    chunks: Iterable[TNumpyArrayNumber],
) -> Iterator[SignalChunk[TNumpyArrayNumber]]:
    frame_idx = 0
    dtype = None
    for chunk in chunks:
        if dtype is None:
            dtype = chunk.dtype
        yield SignalChunk(signal_id=signal_id, frame_idx=frame_idx, array=chunk)
        frame_idx += len(chunk)


TChunkable = TypeVar("TChunkable", bound=Chunkable)


class ArrayBufferingSignalChunker(ABC, Generic[TChunkable]):
    @abstractmethod
    def buffer_and_chunk(
        self,
        inpt_msg: TChunkable,
    ) -> list[TChunkable]:
        """
        does 2 things
        1. "buffer": append inpt_msg to internal buffer
        2. "chunk": emit chunks from internal buffer
        no separation of concerns here, not splitting into two methods to discourage wrong usage
          -> user is "forced" to handle output for every input!
        """
        ...

    def flush_reset_chunker(self) -> list[TChunkable]:
        flushed = self._flush_chunker()
        self.reset_chunker()
        return flushed

    @abstractmethod
    def reset_chunker(self) -> None: ...

    @abstractmethod
    def _flush_chunker(self) -> list[TChunkable]: ...


def update_buffer(buffer: TChunkable | None, inpt_msg: TChunkable) -> TChunkable:
    return (
        buffer.append_chunk(
            inpt_msg,
        )
        if buffer is not None
        else inpt_msg
    )

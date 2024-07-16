import random
from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass

from misc_python_utils.beartypes import NeNpNumberDim1, NpNumber, NpNumberDim1
from numpy.typing import NDArray

from speech_utils.audio_io_utils.audio_array_converters import (
    AudioArrayConverter,
)
from speech_utils.audio_io_utils.audio_utils import break_array_into_chunks


@dataclass
class ClientSideChunkingStrategy:
    """
    supposed to do chunking but might also change data-types from float32 to int16 or whatever
    """

    @abstractmethod
    def chunkit(self, array: NeNpNumberDim1) -> Iterator[NeNpNumberDim1]:
        raise NotImplementedError


@dataclass
class ClientSideFixedSizeChunker(ClientSideChunkingStrategy):
    fixed_size: int = 1000  # samples
    audio_array_converter: AudioArrayConverter | None = None

    def chunkit(self, array: NeNpNumberDim1) -> Iterator[NeNpNumberDim1]:
        processed_array = (
            self.audio_array_converter.convert_array(array)
            if self.audio_array_converter
            else array
        )
        yield from break_array_into_chunks(
            processed_array,
            chunk_size=self.fixed_size,
        )


@dataclass
class ClientSideRandomSizeChunker(ClientSideChunkingStrategy):
    sample_rate: int = 16000
    random_minmax_chunk_dur: tuple[float, float] = (0.1, 1.0)

    @abstractmethod
    def chunkit(self, array: NDArray[NpNumber]) -> Iterator[NDArray[NpNumber]]:
        yield from break_array_into_randomly_sized_chunks(
            array,
            round(self.random_minmax_chunk_dur[0] * self.sample_rate),
            round(self.random_minmax_chunk_dur[1] * self.sample_rate),
        )


def break_array_into_randomly_sized_chunks(
    array: NpNumberDim1,
    min_size: int,
    max_size: int,
) -> Iterator[NpNumberDim1]:
    """
    non-overlapping chunks
    """
    buffer = array.copy()
    while len(buffer) > 0:
        chunk_size = random.randint(min_size, max_size)
        out = buffer[:chunk_size]
        buffer = buffer[chunk_size:]
        yield out

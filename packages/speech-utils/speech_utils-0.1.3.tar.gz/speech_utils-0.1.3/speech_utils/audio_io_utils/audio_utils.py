from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, TypeVar

import numpy as np
from misc_python_utils.beartypes import (
    NeNpFloatDim1,
    NpFloat32Dim1,
    NpFloatDim1,
    NpNumber,
    NpNumberDim1,
    NumpyInt16Dim1,
)
from numpy.typing import NDArray

MAX_16_BIT_PCM: float = float(2**15) - 1  # 32_768 - 1 for 16 bit, -1 for the zero

TorchTensor = (
    Any  # TODO: how can I hint for this if it is an extra/optional dependency?
)


def get_first_channel(
    signal: NDArray | TorchTensor,
) -> NDArray | TorchTensor:
    if len(signal.shape) == 2:  # noqa: PLR2004
        channel_dim = np.argmin(signal.shape)
        first_channel = 0
        if channel_dim == 0:
            signal = signal[first_channel, :]
        else:
            signal = signal[:, first_channel]
    elif len(signal.shape) == 1:
        pass
    else:
        msg = "how to handle 3dim arrays?"
        raise NotImplementedError(msg)

    return signal.squeeze()  # pyright: ignore [reportUnknownVariableType]


def convert_to_int16_array(a: NpNumberDim1) -> NumpyInt16Dim1:
    """
    TODO: caution this is NOT loss-less but destroying information!
    """
    a = a / np.max(np.abs(a)) * MAX_16_BIT_PCM
    return a.astype(np.int16)


def convert_int16_to_float(audio: NumpyInt16Dim1) -> NpFloatDim1:
    return audio.astype(np.float32) / MAX_16_BIT_PCM


def _convert_samples_to_float32(samples: NDArray[NpNumber]) -> NDArray[np.float32]:  # pyright: ignore [reportUnusedFunction]
    """
    TODO: caution this is NOT loss-less but destroying information!
    stolen from nemo
    Convert sample type to float32.
    Audio sample type is usually integer or float-point.
    Integers will be scaled to [-1, 1] in float32.
    """
    float32_samples = samples.astype("float32")
    if np.issubdtype(samples.dtype, np.integer):
        bits = samples.dtype.itemsize * 8
        float32_samples *= 1.0 / 2 ** (bits - 1)
    elif np.issubdtype(samples.dtype, np.floating):  # noqa: NPY201
        pass
    else:
        raise TypeError(  # noqa: TRY003
            f"Unsupported sample type: {samples.dtype}."  # noqa: COM812, EM102
        )  # noqa: EM102, TRY003
    return float32_samples


TNumpyArrayNumber = TypeVar("TNumpyArrayNumber", bound=NDArray[NpNumber])


def break_array_into_chunks(
    array: TNumpyArrayNumber,
    chunk_size: int,
) -> Iterator[TNumpyArrayNumber]:
    """
    non-overlapping chunks
    """
    buffer = array.copy()
    while len(buffer) > 0:
        out = buffer[:chunk_size]
        buffer = buffer[chunk_size:]
        # TODO: somehow pyright does not get it!
        yield out  # pyright: ignore [reportReturnType]


def normalize_audio_array(
    array: NpNumberDim1,
    gain: float = 0.8,  # to avoid saturation while writing to wav
) -> NeNpFloatDim1:
    """
    copypasted from nvidia/nemo: TranscodePerturbation
    """
    array_f = array.astype(float)

    max_level = np.max(np.abs(array_f))
    if max_level > 0.8:  # noqa: PLR2004
        norm_factor = gain / max_level
        norm_samples = norm_factor * array_f
    else:
        norm_samples = array_f
    return norm_samples


@dataclass(slots=True)
class AudioResampler:
    # TODO(tilo): rename this cause it namelcashes with pyav's resampler
    @abstractmethod
    def resample(
        self,
        audio: NpFloat32Dim1,
        sample_rate: int,
        target_sample_rate: int,
    ) -> NpFloat32Dim1: ...

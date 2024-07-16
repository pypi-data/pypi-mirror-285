from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar

import numpy as np
from misc_python_utils.beartypes import (
    NeNpFloat32Dim1,
    NeNpInt16Dim1,
    NeNpNumberDim1,
    NpNumber,
)

from speech_utils.audio_io_utils.audio_utils import (
    convert_int16_to_float,
    convert_to_int16_array,
)


@dataclass(slots=True)
class AudioArrayConverter:
    input_dtype: ClassVar[type[NpNumber]] = np.int16

    def convert_bytes(self, bytes_: bytes) -> NeNpNumberDim1:
        return self.convert_array(np.frombuffer(bytes_, dtype=self.input_dtype))

    @abstractmethod
    def convert_array(self, audio_array: NeNpNumberDim1) -> NeNpNumberDim1: ...


@dataclass(slots=True)
class Float32ToInt16Converter(AudioArrayConverter):
    input_dtype: ClassVar[type[NpNumber]] = np.float32

    def convert_array(self, audio_array: NeNpNumberDim1) -> NeNpInt16Dim1:  # noqa: PLR6301
        return convert_to_int16_array(audio_array)


@dataclass(slots=True)
class Int16ToFloat32Converter(AudioArrayConverter):
    input_dtype: ClassVar[type[NpNumber]] = np.int16

    def convert_array(self, audio_array: NeNpInt16Dim1) -> NeNpFloat32Dim1:  # noqa: PLR6301
        return convert_int16_to_float(audio_array)


@dataclass(slots=True)
class AlreadyIsFloat32(AudioArrayConverter):
    input_dtype: ClassVar[type[NpNumber]] = np.float32

    def convert_array(self, audio_array: NeNpFloat32Dim1) -> NeNpFloat32Dim1:  # noqa: PLR6301
        return audio_array

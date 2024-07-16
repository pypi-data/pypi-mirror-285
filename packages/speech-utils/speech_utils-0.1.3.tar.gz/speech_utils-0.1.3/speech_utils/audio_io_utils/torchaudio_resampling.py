from dataclasses import dataclass
from functools import lru_cache

import torch
import torchaudio
from misc_python_utils.beartypes import NpFloat32Dim1, TorchTensor1D
from torch import float32
from torchaudio.transforms import Resample

from speech_utils.audio_io_utils.audio_utils import AudioResampler

torchaudio.utils.sox_utils.set_buffer_size(
    16000,
)  # necessary for long audio-headers (mp3)


@dataclass(slots=True)
class TorchaudioResampler(AudioResampler):
    def resample(  # noqa: PLR6301
        self,
        audio: NpFloat32Dim1,
        sample_rate: int,
        target_sample_rate: int,
    ) -> NpFloat32Dim1:
        return torchaudio_resample(
            signal=torch.from_numpy(audio),  # pyright: ignore [reportUnknownMemberType]
            sample_rate=sample_rate,
            target_sample_rate=target_sample_rate,
        ).numpy()


def torchaudio_resample(
    signal: TorchTensor1D,
    sample_rate: int,
    target_sample_rate: int,
) -> TorchTensor1D:
    if target_sample_rate != sample_rate:
        resampler = get_resampler(
            sample_rate,
            target_sample_rate=target_sample_rate,
            dtype=float32,
        )
        signal = resampler(signal)
    return signal


RESAMPLERS: dict[str, Resample] = {}


@lru_cache(maxsize=20)
def get_resampler(
    sample_rate: int,
    target_sample_rate: int,
    dtype: torch.dtype | None,
) -> Resample:
    return Resample(sample_rate, target_sample_rate, dtype=dtype)

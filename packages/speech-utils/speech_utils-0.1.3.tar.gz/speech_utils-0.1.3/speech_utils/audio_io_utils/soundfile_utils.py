from dataclasses import dataclass
from io import BytesIO

import librosa
import numpy as np
import soundfile
from misc_python_utils.beartypes import NeNpFloatDim1, NpFloat32Dim1

from speech_utils.audio_io_utils.audio_utils import (
    AudioResampler,
    _convert_samples_to_float32,  # noqa: PLC2701
)


@dataclass(slots=True)
class LibrosaResampler(AudioResampler):
    def resample(  # noqa: PLR6301
        self,
        audio: NpFloat32Dim1,
        sample_rate: int,
        target_sample_rate: int,
    ) -> NpFloat32Dim1:
        return (
            librosa.core.resample(  # noqa: F821
                audio,
                orig_sr=sample_rate,
                target_sr=target_sample_rate,
            )
            if sample_rate != target_sample_rate
            else audio
        )


def load_resample_with_soundfile(  # noqa: C901, PLR0913, PLR0917
    audio_file: str | BytesIO,
    target_sr: int | None = None,  # TODO: rename to target_sample_rate
    int_values: bool = False,
    offset: float | None = None,
    duration: float | None = None,
    trim: bool = False,
    trim_db: int = 60,
) -> NeNpFloatDim1:
    """
    based on nemo code: https://github.com/NVIDIA/NeMo/blob/aff169747378bcbcec3fc224748242b36205413f/nemo/collections/asr/parts/preprocessing/segment.py#L173
    """
    with soundfile.SoundFile(audio_file, "r") as f:  # noqa: F821
        dtype = "int32" if int_values else "float32"
        sample_rate = f.samplerate
        if offset is not None:
            f.seek(int(offset * sample_rate))
        if duration is not None:
            samples = f.read(int(duration * sample_rate), dtype=dtype)
        else:
            samples = f.read(dtype=dtype)

    samples = (
        samples.transpose()
    )  # channels in first, signal in second axis, thats how librosa wants it

    samples = _convert_samples_to_float32(samples)
    if target_sr is not None and target_sr != sample_rate:
        samples = librosa.core.resample(  # noqa: F821
            samples,
            orig_sr=sample_rate,
            target_sr=target_sr,
        )
    if trim:
        samples, _ = librosa.effects.trim(samples, top_db=trim_db)  # noqa: F821
    if samples.ndim >= 2:  # noqa: PLR2004
        # here was bug in nemo-code!
        # explanation: resampy does resample very last axis, see: https://github.com/bmcfee/resampy/blob/29d34876a61fcd74e72003ceb0775abaf6fdb961/resampy/core.py#L15
        # resample(x, sr_orig, sr_new, axis=-1, filter='kaiser_best', **kwargs):
        assert samples.shape[0] < samples.shape[1]
        samples = np.mean(samples, 0)
    return samples

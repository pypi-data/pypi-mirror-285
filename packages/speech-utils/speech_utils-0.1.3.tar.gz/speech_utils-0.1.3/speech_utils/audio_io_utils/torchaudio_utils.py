from collections.abc import Iterator
from dataclasses import dataclass
from io import BytesIO
from os import PathLike
from tempfile import NamedTemporaryFile
from typing import Any, BinaryIO

import torchaudio
from misc_python_utils.beartypes import File, NeNpFloatDim1, TorchTensor1D
from misc_python_utils.processing_utils.processing_utils import exec_command

from speech_utils.audio_io_utils.audio_utils import (
    break_array_into_chunks,
    get_first_channel,
)
from speech_utils.audio_io_utils.torchaudio_resampling import torchaudio_resample

torchaudio.utils.sox_utils.set_buffer_size(
    16000,
)  # necessary for long audio-headers (mp3)


def ffmpeg_torch_load(
    file: File,
    target_sample_rate: int = 16000,
) -> TorchTensor1D:
    """
    TODO: this is super ugly, why cant I load with librosa? or another ffmpeg wrapper
    """
    # name = Path(file).stem
    with NamedTemporaryFile(
        # prefix=name.replace(" ", "_"),
        suffix=".wav",
        delete=True,
    ) as tmp_wav:
        cmd = f'ffmpeg -i "{file}" -ac 1 -ar {target_sample_rate} {tmp_wav.name} -y'
        _o, _e = exec_command(cmd)

        return load_resample_with_torch(
            data_source=tmp_wav.name,
            target_sample_rate=target_sample_rate,
        )


def read_audio_chunks_from_file(
    audio_filepath: str,
    target_sample_rate: int,
    offset: float = 0.0,
    duration: float | None = None,
    chunk_duration: float = 0.05,
) -> Iterator[NeNpFloatDim1]:
    """
    formerly named resample_stream_file
    """
    array = load_resample_with_torch(
        data_source=audio_filepath,
        target_sample_rate=target_sample_rate,
        offset=offset,
        duration=duration,
    )
    return break_array_into_chunks(
        array.numpy(),
        int(target_sample_rate * chunk_duration),
    )


def load_resample_with_torch(  # noqa: PLR0913, PLR0917
    data_source: Any,  # ExFileObject
    format_: str | None = None,
    sample_rate: int | None = None,
    target_sample_rate: int | None = 16000,
    offset: int | float | None = None,
    duration: int | float | None = None,
) -> TorchTensor1D:  # TODO: somehow pycharm does not understand this type hint
    """
    Providing num_frames and frame_offset arguments will slice the resulting Tensor object while decoding.
    :param duration: see: .../torchaudio/backend/sox_io_backend.py
    """
    data = torchaudio_load(
        data_source,
        offset,
        duration,
        format_,
        sample_rate,
    )
    return torchaudio_resample(
        data.array.squeeze(),
        data.sample_rate,
        target_sample_rate,
    )


@dataclass
class TorchAudioData:
    array: TorchTensor1D
    sample_rate: int


def torchaudio_load(
    # see: https://pytorch.org/audio/main/generated/torchaudio.info.html
    data_source: BinaryIO | str | PathLike,  # pyright: ignore [reportMissingTypeArgument, reportUnknownParameterType]
    offset: int | float | None = None,
    duration: int | float | None = None,
    format_: str | None = None,
    sample_rate: int | None = None,
) -> TorchAudioData:
    if isinstance(data_source, BytesIO):
        assert format_ is not None, "when reading from BytesIO a format must be given"
    if sample_rate is None and offset is not None:
        sample_rate = torchaudio_info(data_source).sample_rate
    signal, sample_rate = torchaudio.load(
        data_source,
        format=format_,
        frame_offset=_parse_offset_for_torchaudio_load(offset, sample_rate),
        num_frames=_parse_duration_for_torchaudio_load(duration, sample_rate),
    )

    signal = get_first_channel(signal)
    assert (
        len(signal) > 1000  # noqa: PLR2004
    ), f"{data_source=} below 1k samples is not really a signal!"
    return TorchAudioData(signal, sample_rate)


def _parse_offset_for_torchaudio_load(
    offset: int | float | None,
    sample_rate: int | None = None,
) -> int:
    if offset is None:
        frame_offset = 0
    elif isinstance(offset, float):
        assert sample_rate is not None
        frame_offset = round(offset * sample_rate)
    else:
        frame_offset = offset
    return frame_offset


def _parse_duration_for_torchaudio_load(
    duration: int | float | None,
    sample_rate: int | None = None,
) -> int:
    if duration is None:
        num_frames = -1
    elif isinstance(duration, float):
        assert sample_rate is not None
        num_frames = round(duration * sample_rate)
    else:  # isinstance(duration, int):
        num_frames = duration
    return num_frames


@dataclass(slots=True, frozen=True)
class TorchAudioInfo:
    num_frames: int
    sample_rate: int

    @property
    def duration(self) -> float:
        return self.num_frames / self.sample_rate


def torchaudio_info(audio_file: BinaryIO | str | PathLike) -> TorchAudioInfo:
    info = torchaudio.info(audio_file)
    return TorchAudioInfo(info.num_frames, info.sample_rate)

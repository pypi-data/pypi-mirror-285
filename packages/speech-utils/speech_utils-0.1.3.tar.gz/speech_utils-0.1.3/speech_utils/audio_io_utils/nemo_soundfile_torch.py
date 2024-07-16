import logging
from io import BytesIO
from typing import Any

from misc_python_utils.beartypes import NeNpFloatDim1

from speech_utils.audio_io_utils.nemo_audio_utils import load_resample_with_nemo
from speech_utils.audio_io_utils.soundfile_utils import (
    load_resample_with_soundfile,
)
from speech_utils.audio_io_utils.torchaudio_utils import load_resample_with_torch

logger = logging.getLogger(__name__)

SMALL_NUBMER_OF_SAMPLES = 1000


def load_audio_array_from_filelike(  # noqa: PLR0913, PLR0917
    audio_source: Any,
    audio_format: str,
    target_sample_rate: int,
    sample_rate: int | None = None,
    offset: float = 0.0,
    duration: float | None = None,
) -> NeNpFloatDim1:
    """
    TODO(tilo): this is old copypaste code, do I really need this function -> refactor move upstream
    """
    # TODO: WTF why is fisher faster with nemo, but kaldi which is also wav, faster with torchaudio??
    if audio_format == "wav" and not any(s in audio_source for s in ["Fisher"]):
        array = load_resample_with_nemo(
            audio_filepath=audio_source,
            offset=offset,
            duration=duration,
            target_sample_rate=target_sample_rate,
        )

    elif audio_format == "flac":
        # TODO: torchaudio cannot load flacs?
        #   nemo cannot properly handle multi-channel flacs
        audio_source = (
            audio_source
            if isinstance(audio_source, str)
            else BytesIO(audio_source.read())
        )
        array = load_resample_with_soundfile(
            audio_file=audio_source,
            target_sr=target_sample_rate,
            offset=offset,
            duration=duration,
        )
    else:
        torch_tensor = load_resample_with_torch(
            data_source=audio_source,
            sample_rate=sample_rate,
            target_sample_rate=target_sample_rate,
            offset=offset if offset > 0.0 else None,
            duration=duration,
            format_=audio_format,
        )
        array = torch_tensor.numpy()

    if len(array) < SMALL_NUBMER_OF_SAMPLES:
        logger.warning(
            f"{audio_source=},{offset=},{duration=} below 1k samples is not really a signal!",
        )
    return array

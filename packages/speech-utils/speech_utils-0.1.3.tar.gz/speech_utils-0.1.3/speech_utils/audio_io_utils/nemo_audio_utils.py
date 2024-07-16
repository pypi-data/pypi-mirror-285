from io import BytesIO

from misc_python_utils.beartypes import NeNpFloatDim1

from speech_utils.audio_io_utils.audio_utils import get_first_channel


def load_resample_with_nemo(
    audio_filepath: str | BytesIO,
    target_sample_rate: int | None = 16000,
    offset=0.0,  # noqa: ANN001
    duration: float | None = None,
) -> NeNpFloatDim1:
    from nemo.collections.asr.parts.preprocessing import AudioSegment  # noqa: PLC0415

    # cause nemo wants 0 if no duration
    duration = 0 if duration is None else duration
    audio = AudioSegment.from_file(
        audio_filepath,
        target_sr=target_sample_rate,
        offset=offset,
        duration=duration,
        trim=False,
    )
    signal = audio.samples
    signal = get_first_channel(signal)
    assert (
        len(signal) > 1000  # noqa: PLR2004
    ), f"{audio_filepath=} below 1k samples is not really a signal!"
    assert len(audio.samples.shape) == 1, f"{len(audio.samples.shape)=}"
    return signal

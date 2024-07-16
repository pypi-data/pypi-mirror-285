from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Annotated

from misc_python_utils.beartypes import NeNpFloatDim1

from speech_utils.audio_io_utils.audio_utils import break_array_into_chunks
from speech_utils.audio_io_utils.soundfile_utils import (
    load_resample_with_soundfile,
)
from speech_utils.data_models.audio_array_models import (
    NeMsTimeSpanAudioArray,
)
from speech_utils.signal_chunking.signal_chunker import (
    SignalChunk,
    signal_chunks_from_arrays,
)

PositiveFloat = Annotated[float, lambda x: x > 0]


@dataclass
class AudioSignalChunk(NeMsTimeSpanAudioArray, SignalChunk[NeNpFloatDim1]):
    """
    formerly called: AudioMessageChunk
    instance of this represents one chunks of an audio-message
    an audio-message can be split into possibly overlapping chunks, entire message got one message_id
    frame_idx is counter/absolut-position of audio-chunk's start frame in entire audio-message
    """

    start: PositiveFloat = field(init=False)
    end: PositiveFloat = field(init=False)

    def _parse_validate_data(self) -> None:
        self.start = self.frame_idx / self.sample_rate
        self.end = self.start + len(self.array) / self.sample_rate
        super()._parse_validate_data()


def audio_chunks_from_file(
    audio_filepath: str,
    client_sample_rate: int,
    chunk_duration: float = 0.1,
) -> Iterator[AudioSignalChunk]:
    # TODO: use "decode_audio" from faster-whisper which underthehood uses pyav?

    array = load_resample_with_soundfile(
        audio_file=audio_filepath,
        target_sr=client_sample_rate,
    )
    chunks = break_array_into_chunks(
        array,
        int(client_sample_rate * chunk_duration),
    )
    yield from audio_chunks_from_arrays(audio_filepath, chunks, client_sample_rate)


def audio_chunks_from_arrays(
    signal_id: str,
    arrays: Iterable[NeNpFloatDim1],
    sample_rate: int,
) -> Iterator[AudioSignalChunk]:
    # old name: audio_messages_from_chunks
    for _chunk_idx, m in enumerate(signal_chunks_from_arrays(signal_id, arrays)):
        assert len(m.array) > 0
        yield AudioSignalChunk(
            signal_id=m.signal_id,
            frame_idx=m.frame_idx,
            array=m.array,
            sample_rate=sample_rate,
        )

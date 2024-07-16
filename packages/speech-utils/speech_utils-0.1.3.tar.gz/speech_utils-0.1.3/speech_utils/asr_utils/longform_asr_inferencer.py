from dataclasses import dataclass, field

from buildable_dataclasses.buildable import Buildable
from misc_python_utils.slugification import CasedNameSlug

from speech_utils.asr_utils.accumulating_asr_streamer import (
    AccumulatingASRStreamInferencer,
)
from speech_utils.asr_utils.accumulating_longform_asr_inferencer import (
    AccumulatingLongformASRInferencer,
)
from speech_utils.asr_utils.clientside_chunking_strategies import (
    ClientSideChunkingStrategy,
    ClientSideFixedSizeChunker,
)
from speech_utils.asr_utils.inferencer_interfaces import (
    AudioArray2SegmentedTranscripts,
)
from speech_utils.asr_utils.streaming_asr_utils import (
    END_OF_AUDIO_STREAM,
    StreamingASRMessage,
)
from speech_utils.audio_segmentation_utils.non_overlapping_segments_variations import (
    TextNeNoSeg,
)
from speech_utils.data_models.audio_array_models import AudioArray
from speech_utils.data_models.misc_data_types import EmptySeq
from speech_utils.data_models.timespans_with_text import MsTimeSpanNeText
from speech_utils.signal_chunking.audio_signal_chunk import (
    AudioSignalChunk,
    audio_chunks_from_arrays,
)


@dataclass
class AccumASRStreamerAA2ST(
    Buildable,
    AudioArray2SegmentedTranscripts[MsTimeSpanNeText],
):
    """
    TODO: rename to StreamerAsLongFormASRInferencer?
    essentially wraps a streaming-asr-inferencer into an "offline" inferencer -> long-form ASR
    """

    inferencer: AccumulatingASRStreamInferencer[MsTimeSpanNeText]
    client_side_chunker: ClientSideChunkingStrategy = field(
        default_factory=lambda: ClientSideFixedSizeChunker(
            fixed_size=1000,  # does not really matter, gets rechunked by inferencer anyhow
            audio_array_converter=None,
        ),
    )
    name: CasedNameSlug = field(init=False)

    def __post_init__(self):
        self.name = f"streaming-asr-{self.inferencer.name}"

    # no need for enter-exit already done by ClientServiceExca

    def audio_to_segmented_transcripts(
        self,
        audio_array: AudioArray,
    ) -> TextNeNoSeg[MsTimeSpanNeText] | EmptySeq[MsTimeSpanNeText]:
        chunks = self.client_side_chunker.chunkit(audio_array.array)
        audio_chunks = list(
            audio_chunks_from_arrays(
                signal_id="nobody_cares",
                arrays=chunks,  # pyright: ignore [reportArgumentType]
                sample_rate=audio_array.sample_rate,
            ),
        )
        with self.inferencer:
            outputs: list[StreamingASRMessage[MsTimeSpanNeText]] = [
                t
                for inpt in [*audio_chunks, END_OF_AUDIO_STREAM]
                for t in self.inferencer.stream_infer_cumulative(inpt)
            ]

        if len(outputs) > 0:  # noqa: SIM108
            out = outputs[-1].segments
        else:
            out = EmptySeq[MsTimeSpanNeText]()

        return out


@dataclass
class LongFormASRInferencer(Buildable, AudioArray2SegmentedTranscripts):
    inferencer: AccumulatingLongformASRInferencer
    name: CasedNameSlug = field(init=False)

    def __post_init__(self):
        self.name = f"streaming-asr-{self.inferencer.name}"

    # no need for enter-exit already done by ClientServiceExca

    def audio_to_segmented_transcripts(
        self,
        audio_array: AudioArray,
    ) -> TextNeNoSeg | None:
        audio_chunks = [
            AudioSignalChunk(
                signal_id="nobody_cares",
                frame_idx=0,
                array=audio_array.array,
                sample_rate=audio_array.sample_rate,
            ),
        ]
        out = self.inferencer.longform_infer_cumulative(audio_chunks)
        return TextNeNoSeg(list(out)) if len(out) > 0 else None

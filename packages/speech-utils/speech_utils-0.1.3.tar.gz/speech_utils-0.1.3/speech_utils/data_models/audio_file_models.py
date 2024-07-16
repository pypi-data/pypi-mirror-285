from dataclasses import dataclass
from typing import ClassVar

from misc_python_utils.prefix_suffix import PrefixSuffix

from speech_utils.data_models.coop_mixin_data_models import (
    Duration,
    SampleRate,
    Segment,
)
from speech_utils.data_models.timespans_with_text import SampleId, Text
from speech_utils.data_models.tofrom_dict_psfile import ToFromDictPsFile


@dataclass(kw_only=True)
class AudioFile(ToFromDictPsFile):
    audio_file: PrefixSuffix
    _attr_name: ClassVar[str] = "audio_file"


@dataclass(kw_only=True)
class AudioSample(SampleId, AudioFile):
    pass


@dataclass(kw_only=True)
class TranscribedAudioFileSegment(Text, AudioFile, Segment):
    pass


@dataclass(kw_only=True)
class TranscribedAudioFileSegmentWithSamplerate(
    TranscribedAudioFileSegment,
    SampleRate,
):
    pass


# TranscribedAudioFileSegmentType = Annotated[
#     PsFile | Text | Segment,
#     IsInstance[Segment] & IsInstance[PsFile] & IsInstance[Text],
# ]


@dataclass(kw_only=True)
class TranscribedAudioFile(SampleId, SampleRate, AudioFile, Text):
    pass


@dataclass(kw_only=True)
class AudioFileSample(SampleId, SampleRate, AudioFile):
    pass


@dataclass(kw_only=True)
class AudioFileDurationSample(SampleId, Duration, SampleRate, AudioFile):
    pass


@dataclass(kw_only=True)
class AudioFileSegment(Segment, SampleRate, AudioFile):
    pass


ASRSample = TranscribedAudioFileSegment

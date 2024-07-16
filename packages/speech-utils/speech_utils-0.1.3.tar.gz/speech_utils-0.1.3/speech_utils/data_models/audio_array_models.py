from dataclasses import dataclass

from misc_python_utils.beartypes import NeNpFloatDim1
from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    CoopDataValidationError,
)

from speech_utils.data_models.coop_mixin_data_models import (
    SampleRate,
)
from speech_utils.data_models.time_spans import NeMsTimeSpan
from speech_utils.data_models.timespans_with_text import (
    NeMsTimeSpanText,
    SampleId,
    Text,
)


@dataclass
class MonoChannelNonEmptyNumpyArray:
    array: NeNpFloatDim1


@dataclass
class AudioArray(SampleRate, MonoChannelNonEmptyNumpyArray):
    @property
    def duration(self) -> float:
        return len(self.array) / self.sample_rate


@dataclass
class AudioArrayText(AudioArray, Text):
    pass


@dataclass
class IdAudioArray(AudioArray, SampleId):
    pass


@dataclass
class IdAudioArrayText(AudioArrayText, SampleId):
    pass


ONE_MS = 0.001


@dataclass(kw_only=True)
class NeMsTimeSpanAudioArray(NeMsTimeSpan, AudioArray):
    def _parse_validate_data(self) -> None:
        if abs(self.duration - len(self.array) / self.sample_rate) > 2 * ONE_MS:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.duration=} != {len(self.array) / self.sample_rate=}",  # noqa: EM102
            )
        super()._parse_validate_data()


@dataclass(kw_only=True)
class NeMsTimeSpanTextAudioArray(NeMsTimeSpanText, NeMsTimeSpanAudioArray):
    pass

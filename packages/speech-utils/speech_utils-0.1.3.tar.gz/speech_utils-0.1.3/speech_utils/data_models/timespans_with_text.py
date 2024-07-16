from dataclasses import dataclass
from typing import TypeVar

from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import ToFromDictCoopMixin
from nested_dataclass_serialization.dataclass_serialization_utils import NeStr
from typing_extensions import Protocol, Self, runtime_checkable

from speech_utils.data_models.time_spans import (
    MsTimeSpan,
    NeMsTimeSpan,
    NeTimeSpan,
    Seconds,
    TimeSpan,
)


@dataclass
class SampleId:
    sample_id: NeStr


@dataclass
class Text(ToFromDictCoopMixin):
    """
    text instead of transcript makes it more general but also takes away semantics
    """

    text: str


@dataclass
class IdText(Text, SampleId):
    pass


@dataclass
class NeText(Text):
    text: NeStr


@dataclass(kw_only=True)
class Transcript:
    transcript: str


@dataclass(kw_only=True)
class TimeSpanText(Text, TimeSpan):
    @classmethod
    def merge(cls, first: Self, second: Self) -> Self:
        start = min(first.start, second.start)
        end = max(first.end, second.end)
        return cls(start=start, end=end, text=first.text + second.text)


@runtime_checkable
class TimeSpanTextP(Protocol):
    start: float
    end: float
    text: str

    @property
    def duration(self) -> Seconds: ...

    # TODO: what about merge and _parse_validate_data?


TTimeSpanTextP = TypeVar("TTimeSpanTextP", bound=TimeSpanTextP)


StartEndText = TimeSpanText


@dataclass(kw_only=True)
class MsTimeSpanText(TimeSpanText, MsTimeSpan):  # the MRO does not matter
    pass


@dataclass(kw_only=True)
class TimeSpanNeText(NeText, TimeSpanText):
    # allow segments to be empty, not nice but thats what whisper gives us
    pass


@dataclass(kw_only=True)
class MsTimeSpanNeText(
    NeText,
    MsTimeSpanText,
    TimeSpanText,
):  # having to inherit from TimeSpanText seems redundant but is neccessary -> curse of multi-inheritance
    # allow segments to be empty, not nice but thats what whisper gives us
    pass


@dataclass(kw_only=True)
class NeTimeSpanNeText(NeText, NeTimeSpan, TimeSpanText):
    """
    time-span AND text are non-empty!
    """


NeTimeSpanText = NeTimeSpanNeText


@dataclass(kw_only=True)
class NeMsTimeSpanNeText(
    NeMsTimeSpan,
    NeTimeSpanNeText,
    NeText,
    TimeSpanText,
):  # WTF! right in the multi-inheritance hell! would not be necessary if I used protocols for "type-intersections"
    """
    time-span AND text are non-empty!
    """


NeMsTimeSpanText = NeMsTimeSpanNeText

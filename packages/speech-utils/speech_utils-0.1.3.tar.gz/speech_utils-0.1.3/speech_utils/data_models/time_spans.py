import logging
import typing
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    CoopDataValidationError,
    DataValidationCoopMixinBase,
)
from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import ToDictCoopMixin
from typing_extensions import Self

from speech_utils.data_models.misc_data_types import PositiveTimeStamp

logger = logging.getLogger(__name__)

Seconds = float


@dataclass
class TimeSpan(DataValidationCoopMixinBase, ToDictCoopMixin):
    """
    this is a hybrid between parsing and validating
    start/end are validated via beartype -> at runtime
    the TimeSpan-class itself is "parsed" -> at "complile-time" (not at runtime)
    """

    start: PositiveTimeStamp
    end: PositiveTimeStamp

    def _parse_validate_data(self) -> None:
        self.start = float(self.start)
        self.end = float(self.end)  # convert numpy.float64 -> float

        if self.start < 0 or self.end < self.start:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.start=} > {self.end=}"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()  # noqa: UP008

        # rounding else-where might lead to start==end, relaxing here cause it makes no sense for letter/character-wise (interpolated)

    @property
    def duration(self) -> Seconds:
        return self.end - self.start

    @classmethod
    def merge(cls, first: Self, second: Self) -> Self:
        start = min(first.start, second.start)
        end = max(first.end, second.end)
        return cls(start=start, end=end)

    def _to_dict(self) -> dict[str, Any]:
        return super()._to_dict() | {
            "start": round(self.start, 6),
            "end": round(self.end, 6),
        }


@runtime_checkable
class TimeSpanP(Protocol):
    start: float
    end: float

    @property
    def duration(self) -> Seconds: ...

    # TODO: what about merge and _parse_validate_data?


TTimeSpanP = typing.TypeVar("TTimeSpanP", bound=TimeSpanP)


class HasNonZeroDuration(DataValidationCoopMixinBase):
    @property
    @abstractmethod
    def duration(self) -> Seconds: ...

    def _parse_validate_data(self) -> None:
        if self.duration <= 0.0:  # noqa: PLR2004
            raise CoopDataValidationError(f"{self.duration=}")  # noqa: EM102
        super()._parse_validate_data()  # noqa: UP008


@dataclass
class NeTimeSpan(TimeSpan, HasNonZeroDuration):
    pass


NeStartEnd = NeTimeSpan


@dataclass
class MsTimeSpan(TimeSpan):
    """
    milliseconds time span
    TODO: floats are rounded here! thats bad, it should rather contain start/end information as integers (milliseconds)
    """

    def _parse_validate_data(self) -> None:
        self.start = round(
            float(
                self.start,
            ),  # TODO: it seemed that np.float was given and beartype did not complain
            3,
        )  # rounding to circumvent rounding-errors! -> maybe I should have taken milliseconds from the very start
        self.end = round(float(self.end), 3)
        super()._parse_validate_data()  # noqa: UP008


@dataclass
class NeMsTimeSpan(MsTimeSpan, NeTimeSpan):
    pass


# TTimeSpan_co = TypeVar("TTimeSpan_co", bound=TimeSpan, covariant=True) # use protocol instead

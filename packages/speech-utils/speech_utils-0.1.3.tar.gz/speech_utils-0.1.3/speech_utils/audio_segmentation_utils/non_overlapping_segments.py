from collections.abc import Iterator, Sequence
from dataclasses import dataclass, fields
from itertools import pairwise
from typing import Any, TypeVar, overload

from misc_python_utils.beartypes import NeSequence
from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    DataValidationCoopMixinBase,
)
from typing_extensions import Self

from speech_utils.audio_segmentation_utils.already_validated_input_data import (
    AlreadyValidatedInputData,
)
from speech_utils.audio_segmentation_utils.non_overlapping import (
    PositiveFloat,
    is_non_overlapping,
    logger,
)
from speech_utils.audio_segmentation_utils.ordered_spans import OrderedOverlappingSpans
from speech_utils.data_models.time_spans import TimeSpan, TTimeSpanP


@dataclass
class NeNoSegments(
    Sequence[TTimeSpanP],  # no NeSequence here, this confuses pycharm
    DataValidationCoopMixinBase,
):
    """
    Non-Empty Non-Overlapping Segments
    enforces+assures non-overlapping segmetns, but seg[i].end is still allowed to be seg[i+].start!
    """

    segments: NeSequence[TTimeSpanP]

    def __setattr__(self, key: str, value: Any) -> None:
        # https://stackoverflow.com/questions/63803794/how-to-freeze-individual-field-of-non-frozen-dataclass
        # stack = inspect.stack()
        # if len(stack) < 2 or stack[1].function != '__init__':
        if hasattr(self, "segments") and key == "segments":
            raise AttributeError("segments is immutable")  # noqa: EM101, TRY003
        super().__setattr__(key, value)

    def _parse_validate_data(self) -> None:
        if len({type(x) for x in self.segments}) > 1:
            raise ValueError(  # noqa: TRY003
                "all elements must be of the same type"  # noqa: COM812, EM101
            )  # noqa: EM101, TRY003

        if not is_non_overlapping(
            self.segments,
        ):
            overlap = [
                (this, next_one)
                for this, next_one in pairwise(self.segments)
                if this.end > next_one.start
            ]
            msg = f"got overlapping segments:{overlap}"
            raise ValueError(msg)  # TODO: raising is bad! handle via Result-type!

        object.__setattr__(self, "segments", tuple(self.segments))  # noqa: PLC2801
        super()._parse_validate_data()  # just to be cooperative

    @overload
    def __getitem__(self, index: int) -> TTimeSpanP: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[TTimeSpanP]: ...

    def __getitem__(self, index):  # pyright: ignore [reportUnknownParameterType]
        return self.segments[index]  # pyright: ignore [reportUnknownVariableType]

    def __len__(self) -> int:
        return len(self.segments)

    def __add__(self, other: Self) -> Self:
        if not (self[-1].end <= other[0].start):
            raise ValueError(  # noqa: TRY003
                f"{self[-1].end=} > {other[0].start=}",  # noqa: EM102
            )
        extra_data = {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name != "segments" and f.init
        }
        if isinstance(self, AlreadyValidatedInputData):
            extra_data["_input_data_is_already_validated"] = True

        return self.create_without_validation(
            list(self.segments) + list(other.segments),
            extra_data=extra_data,
        )

    @classmethod
    def add_offset(
        cls,
        non_overl_segments: Self,
        offset: float,
    ) -> Self:
        # non_overl_segments: Iterable[TTimeSpanP] # was just for pycharm
        offsetted_segments = [
            type(seg)(
                **seg.to_dict()
                | {"start": seg.start + offset, "end": seg.end + offset},
            )
            for seg in non_overl_segments
        ]
        extra_data = {
            f.name: getattr(non_overl_segments, f.name)
            for f in fields(non_overl_segments)
            if f.name != "segments" and f.init
        }
        # if non_overl_segments has init-variable of this name
        if isinstance(non_overl_segments, AlreadyValidatedInputData):
            extra_data["_input_data_is_already_validated"] = True

        return cls.create_without_validation(offsetted_segments, extra_data)

    @classmethod
    def create_without_validation(
        cls,
        segments: Sequence[TTimeSpanP],
        extra_data: dict[str, Any] | None = None,
    ) -> Self:
        """
        for cases like concatenation where we know that the segments are non-overlapping no extra validation is needed
        """
        extra_data = {} if extra_data is None else extra_data
        obj = cls(segments=[segments[0]], **extra_data)
        object.__setattr__(  # noqa: PLC2801
            obj,
            "segments",
            tuple(segments),
        )  # circumvent frozenness  # noqa: PLC2801
        return obj

    def slice_segments(
        self: Self,
        start: PositiveFloat | None = None,
        end: PositiveFloat | None = None,
    ) -> list[TTimeSpanP]:
        if len(self) > 0:
            ARBITRARY_VALUE = 1.0
            start = 0.0 if start is None else start
            if end is not None:
                assert end >= start, f"{start=},{end=}"
            end = self.segments[-1].end + ARBITRARY_VALUE if end is None else end

            sliced = [
                seg for seg in self if seg.start >= start and seg.end <= end
            ]  # TODO: make end exclusive?
        else:
            sliced = []
        return sliced

    def cut_append(self, other: Self) -> Self:
        sliced = self.slice_segments(end=other.segments[0].start)
        new_segments = list(other.segments)
        return self.create_without_validation(sliced + new_segments)

    @classmethod
    def parse(
        cls,
        segments: OrderedOverlappingSpans[TTimeSpanP],
        the_very_end: float | None = None,
        max_tolerable_overlap: PositiveFloat | None = None,
    ) -> Self:
        return fix_segments_to_non_overlapping(
            cls=cls,
            raw_segments=segments,
            the_very_end=the_very_end,
            max_tolerable_overlap=max_tolerable_overlap,
        )


TNeNoSegments = TypeVar("TNeNoSegments", bound=NeNoSegments)


def fix_segments_to_non_overlapping(
    cls: type[TNeNoSegments],
    raw_segments: OrderedOverlappingSpans[TTimeSpanP],  # make it a Sequence
    verbose: bool = False,
    the_very_end: float | None = None,
    max_tolerable_overlap: PositiveFloat | None = None,
) -> TNeNoSegments:
    """
    based on: get_contiguous_stamps from https://github.com/NVIDIA/NeMo/blob/aff169747378bcbcec3fc224748242b36205413f/nemo/collections/asr/parts/utils/speaker_utils.py#L230
    """
    if the_very_end is not None:
        assert raw_segments[-1].start < the_very_end

    def non_overlapping_g() -> Iterator[TTimeSpanP]:
        new_end = 0.0
        for i in range(len(raw_segments)):
            new_start, new_end = fix_to_non_overlapping_segment(
                this_seg=raw_segments[i],
                next_start=raw_segments[i + 1].start
                if i < len(raw_segments) - 1
                else None,
                previous_end=new_end,
                verbose=verbose,
                max_tolerable_overlap=max_tolerable_overlap,
            )
            raw_segments[i].start = new_start
            raw_segments[i].end = new_end
            yield raw_segments[i]

    return cls(list(non_overlapping_g()))


def fix_to_non_overlapping_segment(  # noqa: E201, W291, PLR0913, PLR0917
    this_seg: TimeSpan,
    next_start: float | None,
    previous_end: float,
    max_tolerable_overlap: PositiveFloat | None = None,
    verbose: bool = True,
    the_very_end: float | None = None,
) -> tuple[float, float]:
    new_start = max(this_seg.start, previous_end)

    is_last = next_start is None
    if next_start is not None and (overlap := (this_seg.end - next_start)) > 0.0:
        if max_tolerable_overlap is not None and overlap > max_tolerable_overlap:
            raise ValueError(  # noqa: TRY003
                f"{ this_seg=}->{ next_start=} overlap: {overlap=}",  # noqa: EM102
            )

        new_end = (this_seg.end + next_start) / 2.0
        if verbose:
            logger.warning(
                f"{ this_seg.end=}->{new_end=}<-{ next_start=}",
            )
    elif is_last and the_very_end is not None and this_seg.end > the_very_end:
        new_end = the_very_end
    else:
        new_end = this_seg.end
    return new_start, new_end


NonOverlapTimeSpans = NeNoSegments

import logging
import typing
from abc import abstractmethod
from collections.abc import Iterable, Sequence

from misc_python_utils.beartypes import NeList, NeSequence
from typing_extensions import Self

from speech_utils.data_models.time_spans import TimeSpanP, TTimeSpanP

logger = logging.getLogger(__name__)


class OrderedSpans(tuple[TTimeSpanP, ...]):
    __slots__ = ()

    def __new__(cls, __iterable: Iterable[TTimeSpanP]):  # noqa: PYI063
        sequence = tuple(__iterable)
        if len(sequence) == 0:
            raise ValueError("empty sequence")  # noqa: EM101, TRY003
        if not segment_starts_are_weakly_monoton_increasing(sequence):
            raise ValueError("segment starts are not sorted")  # noqa: EM101, TRY003
        return super().__new__(cls, sequence)

    @classmethod
    def create_dont_validate(
        cls,
        time_spans: NeList[TTimeSpanP],
    ) -> Self:
        """
        with great power comes great responsibility!
        """
        return super().__new__(cls, time_spans)  # noqa: PGH004 (pycharm complains)

    @classmethod
    @abstractmethod
    def parse(
        cls,
        time_spans: NeSequence[TTimeSpanP],
    ) -> Self:  # sadly pycharm cannot infer the return type here, pyright does!
        """
        https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
        """
        ...


class OrderedByMergingNeighbouringAndDroppingOutliers(OrderedSpans[TTimeSpanP]):
    """
    no full-fledged sorting here! only merging
    """

    @classmethod
    def parse(cls, time_spans: NeSequence[TTimeSpanP]) -> Self:
        order_merged: list[TTimeSpanP] = []
        for seg in time_spans:
            TWO = 2  # 2 away means not a direct neighbor
            if not order_merged:
                order_merged.append(seg)
            elif len(order_merged) >= TWO and seg.start < order_merged[-TWO].start:
                pass  # just drop it! no full fledged bubble-sort here!
            elif seg.start < order_merged[-1].start:
                order_merged[-1] = order_merged[-1].merge(order_merged[-1], seg)
            else:
                order_merged.append(seg)
        order_merged_dropped = OrderedByDroppingSpans[TTimeSpanP].parse(order_merged)
        return super().__new__(
            cls,
            tuple(order_merged_dropped),
        )


class OrderedByDroppingSpans(OrderedSpans[TTimeSpanP]):
    """
    makes starts weakly mononone increasing
    """

    @classmethod
    def parse(cls, time_spans: NeSequence[TTimeSpanP]) -> Self:
        dropped_some = [
            seg
            for k, seg in enumerate(time_spans)
            if k == 0
            or seg.start >= time_spans[k - 1].start  # >= weakly monontone increasing
        ]

        return super().__new__(
            cls,
            tuple(dropped_some),
        )


class SortedSpans(OrderedSpans[TTimeSpanP]):
    @classmethod
    def parse(
        cls,
        time_spans: NeSequence[TTimeSpanP],
    ) -> Self:  # sadly pycharm cannot infer the return type here, pyright does!
        """
        https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
        """
        return super().__new__(  # noqa: PGH004 (pycharm complains)
            cls,
            tuple(sorted(time_spans, key=lambda ws: ws.start)),
        )


class OrderedOverlappingSpans(tuple[TTimeSpanP, ...]):  # noqa: SLOT001
    def __new__(cls, __iterable: Iterable[TTimeSpanP]):  # noqa: PYI063
        sequence = tuple(__iterable)
        if len(sequence) == 0:
            raise ValueError("empty sequence")  # noqa: EM101, TRY003
        if not segment_starts_are_weakly_monoton_increasing(sequence):
            raise ValueError("segment starts are not sorted")  # noqa: EM101, TRY003
        elif not segment_end_are_monoton_increasing(sequence):  # noqa: RET506
            raise ValueError(  # noqa: TRY003
                "some segment ends included in others ",  # noqa: EM101
            )
        return super().__new__(cls, sequence)

    @classmethod
    def create_don_validate(
        cls,
        time_spans: NeList[TTimeSpanP],
    ) -> Self:
        """
        with great power comes great responsibility!
        """
        return super().__new__(cls, time_spans)  # noqa: PGH004 (pycharm complains)

    @classmethod
    def parse(
        cls,
        time_spans: OrderedSpans[TTimeSpanP] | NeSequence[TTimeSpanP],
        the_very_end: float | None = None,
    ) -> Self:  # sadly pycharm cannot infer the return type here, pyright does!
        """
        https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
        """
        if not isinstance(time_spans, OrderedSpans):
            time_spans = OrderedByDroppingSpans[TTimeSpanP].parse(time_spans)
        filtered_segments = [
            seg
            for k, seg in enumerate(time_spans)
            if _is_end_fine(time_spans, k, the_very_end)
        ]
        # if len(filtered_segments) < len(time_spans):
        #     logger.debug(f"{[seg for seg in ]}")
        return cls.create_don_validate(  # TODO: use super().__new__(cls, sequence) here to prevent "extra" validation
            filtered_segments,
        )


"""
def are_weakly_monoton_increasing(seq: Sequence[float]) -> bool:

    if len(seq) > 1:
        is_fine = True
        for k in range(1, len(seq)):
            if seq[k - 1] > seq[k]:
                is_fine = False
                logger.warning(f"sequence is NOT sorted! {k=}: {seq[k - 1]}>{seq[k]=}")
                break
    else:
        is_fine = True
    return is_fine

"""


def segment_starts_are_weakly_monoton_increasing(seq: Sequence[TimeSpanP]) -> bool:
    """
    they can still be overlapping
    """

    if len(seq) > 1:
        is_fine = True
        for k in range(1, len(seq)):
            if (prev_start := seq[k - 1].start) > (start := seq[k].start):
                is_fine = False
                logger.warning(f"sequence is NOT sorted! {k=}: {prev_start}>{start=}")
                break
    else:
        is_fine = True
    return is_fine


def segment_end_are_monoton_increasing(seq: Sequence[TimeSpanP]) -> bool:
    """
    they can still be overlapping
    """

    if len(seq) > 1:
        is_fine = True
        for k in range(1, len(seq)):
            if (seq[k - 1].end) >= (seq[k].end):
                is_fine = False
                logger.warning(
                    f"segment {k=} {(seq[k].start, seq[k].end)} is included in {k - 1=} {(seq[k - 1].start, seq[k - 1].end)}",
                )
                break
    else:
        is_fine = True
    return is_fine


@typing.runtime_checkable
class EndP(typing.Protocol):
    end: float


def _is_end_fine(
    ends: Sequence[EndP],
    k: int,
    the_very_end: float | None,
) -> bool:
    seg = ends[k]
    if k < len(ends) - 1:
        is_fine = seg.end < ends[k + 1].end
    elif the_very_end is not None:
        is_fine = seg.end <= the_very_end
    else:
        is_fine = True

    if not is_fine:
        logger.error(
            f"removed: {seg=} due to {ends[k + 1] if k < len(ends) - 1 else the_very_end}",
        )
    # logger.warning(
    #     f"{seg.end=} is not less than {time_spans[k + 1].end if k < len(time_spans) - 1 else the_very_end}",
    # )
    # logger.warning(
    #     f"{seg=},{time_spans[k + 1] if k < len(time_spans) - 1 else the_very_end}",
    # )
    return bool(is_fine)  # numpy.bool -> bool

import logging
from collections.abc import Sequence
from itertools import pairwise
from typing import Annotated

from beartype.vale import Is

from speech_utils.data_models.time_spans import TimeSpan

logger = logging.getLogger(__name__)


def spans_are_non_overlapping(seq: Sequence[TimeSpan]) -> bool:
    if len(seq) > 1:
        prev_cur: list[tuple[TimeSpan, TimeSpan]] = list(
            pairwise(
                seq,
            ),
        )
        is_fine = all(
            (previous.end <= current.start for previous, current in prev_cur),
        )
    else:
        is_fine = True
    return is_fine


is_non_overlapping = spans_are_non_overlapping


def is_overlapping(span: TimeSpan, next_span: TimeSpan) -> bool:
    return bool(span.end > next_span.start)


PositiveFloat = Annotated[float, Is[lambda x: x >= 0]]

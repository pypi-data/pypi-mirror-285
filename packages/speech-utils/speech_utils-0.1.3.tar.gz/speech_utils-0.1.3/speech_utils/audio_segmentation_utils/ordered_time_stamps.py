from collections.abc import Iterable, Sequence

from misc_python_utils.beartypes import NeList
from typing_extensions import Self


class OrderedTimeStamps(
    tuple[float, ...],
):  # TODO is this really feasible to validate each and every time-stamp?
    __slots__ = ()

    def __new__(cls, __iterable: Iterable[float]):  # noqa: PYI063
        sequence = tuple(__iterable)
        if not is_weakly_monoton_increasing_timeseries(sequence):
            raise ValueError("timestamps are not sorted")  # noqa: EM101, TRY003
        return super().__new__(cls, sequence)

    @classmethod
    def create_dont_validate(
        cls,
        timestamps: NeList[float],
    ) -> Self:
        """
        with great power comes great responsibility!
        """
        return super().__new__(cls, timestamps)

    @classmethod
    def parse(cls, timestamps: NeList[float]) -> Self:
        """
        https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
        """
        return super().__new__(  # noqa: PGH004 (pycharm complains)
            cls,
            tuple(sorted(timestamps)),
        )


def is_weakly_monoton_increasing_timeseries(timestamps: Sequence[float]) -> bool:
    return all(
        timestamps[k + 1] - timestamps[k] >= 0.0 for k in range(len(timestamps) - 1)
    )

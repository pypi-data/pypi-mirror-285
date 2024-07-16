from dataclasses import InitVar, dataclass, field
from typing import Any

from misc_python_utils.dataclass_utils import FixedDict
from typing_extensions import Self

from speech_utils.audio_segmentation_utils.non_overlapping import PositiveFloat
from speech_utils.audio_segmentation_utils.ordered_spans import OrderedOverlappingSpans
from speech_utils.data_models.time_spans import TTimeSpanP


@dataclass
class FrozenFields:
    """
    needs to be last in MRO (inheritance order)
    """

    _frozen: bool = field(init=False, default=False)

    def __setattr__(self, __name: str, __value: Any) -> None:  # noqa: PYI063
        if self._frozen:
            raise AttributeError(f"{__name} is immutable")  # noqa: EM101, EM102, TRY003
        else:  # noqa: RET506
            super().__setattr__(__name, __value)


@dataclass
class DontParseUseParser:
    """
    just to "deactivate" the parse-method and enforce that one instead uses a dedicated Parser
    TODO: if one would switch completely to Parsers than this class would be obsolete
    """

    @classmethod
    def parse(
        cls,
        segments: OrderedOverlappingSpans[TTimeSpanP],  # noqa: ARG003
        the_very_end: float | None = None,  # noqa: ARG003
        max_tolerable_overlap: PositiveFloat | None = None,  # noqa: ARG003
    ) -> Self:
        raise AssertionError(  # noqa: TRY003
            "don't parse but expect already parsed+validated data",  # noqa: EM101
        )  # noqa: EM101, TRY003


@dataclass(kw_only=True)
class AlreadyValidatedInputData(FixedDict, FrozenFields):
    """
    open rebellion against: DataValidationCoopMixinBase
    coop-mixin-based data-validation is obsolete if one trusts that the input-data is already validated!
    """

    _input_data_is_already_validated: InitVar[bool]  # only to remind you to be careful

    def __post_init__(self, _input_data_is_already_validated: bool):
        if not _input_data_is_already_validated:
            raise ValueError(  # noqa: TRY003
                "input data must be validated before creating an instance",  # noqa: EM101
            )  # noqa: EM101, TRY003
        self._frozen = True

    def _parse_validate_data(self) -> None:  # noqa: PLR6301
        raise AssertionError("not needed anymore")  # noqa: EM101, TRY003

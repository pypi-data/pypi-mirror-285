from dataclasses import dataclass

from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    CoopDataValidationError,
    DataValidationCoopMixinBase,
)
from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import ToFromDictCoopMixin
from misc_python_utils.prefix_suffix import PrefixSuffix
from nested_dataclass_serialization.dataclass_serialization_utils import NeStr

from speech_utils.data_models.time_spans import Seconds, TimeSpan
from speech_utils.data_models.timespans_with_text import SampleId
from speech_utils.data_models.tofrom_dict_psfile import ToFromDictPsFile


@dataclass(kw_only=True)
class SegmentId(SampleId, DataValidationCoopMixinBase):
    parent_id: NeStr

    def _parse_validate_data(self) -> None:
        if not self.sample_id.startswith(self.parent_id):
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.sample_id=} does not start with {self.parent_id=}",  # noqa: EM102
            )
        super()._parse_validate_data()

    @property
    def segment_id(self) -> NeStr:
        return self.sample_id.replace(self.parent_id, "")


@dataclass(kw_only=True)
class Segment(TimeSpan, SegmentId, ToFromDictCoopMixin):
    pass


@dataclass
class PsFile(ToFromDictPsFile):
    """
    TODO: the disadvantage of using "flat" multi-inheritance instead of nested composition is that attribut-names are hard-coded!
        what if one wanted two files?
        well in theory one could simply use this PsFile as a nested attribute of another class
    """

    file: PrefixSuffix


@dataclass
class SampleRate:
    sample_rate: int  # TODO: beartype or dedicated class for PositiveInt?


@dataclass(kw_only=True)
class Duration:
    duration: Seconds

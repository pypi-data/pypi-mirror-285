from dataclasses import dataclass
from typing import Any, ClassVar

from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import ToFromDictCoopMixin
from misc_python_utils.prefix_suffix import PrefixSuffix


@dataclass
class ToFromDictPsFile(ToFromDictCoopMixin):
    _attr_name: ClassVar[str] = "file"

    def _to_dict(self) -> dict[str, Any]:
        return super()._to_dict() | {
            self._attr_name: {
                "prefix_key": getattr(self, self._attr_name).prefix_key,
                "suffix": getattr(self, self._attr_name).suffix,
            },
        }

    @classmethod
    def _from_dict(cls, jsn: dict[str, Any]) -> dict[str, Any]:
        return super()._from_dict(jsn) | {
            cls._attr_name: PrefixSuffix(
                prefix_key=jsn[cls._attr_name]["prefix_key"],
                suffix=jsn[cls._attr_name]["suffix"],
            ),
        }

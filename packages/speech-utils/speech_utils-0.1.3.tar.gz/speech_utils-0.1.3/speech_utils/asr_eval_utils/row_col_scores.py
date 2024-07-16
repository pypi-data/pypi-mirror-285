from abc import ABC
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from misc_python_utils.beartypes import NeStr
from misc_python_utils.slugification import SlugStr

SomeNestedDict = dict[str, Any]


@dataclass
class ScoreCollection(ABC):
    namespace: SlugStr  # grouping scores under a namespace/category
    scores: SomeNestedDict = field(default_factory=dict)


@dataclass
class RowCol(ABC):
    row: NeStr
    col: NeStr


@dataclass
class RowColScoreCollections(RowCol):
    score_collections: Iterable[ScoreCollection]

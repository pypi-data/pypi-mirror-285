from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Optional

import diff_match_patch
import editdistance
from buildable_dataclasses.buildable import Buildable
from misc_python_utils.beartypes import NeDict
from misc_python_utils.command_line_styling import (
    CMDLINE_BACKGROUND_COLORS,
    CMDLINE_STYLES,
)
from misc_python_utils.dataclass_utils import UNDEFINED

name2bg = {}

DIFF_DELETE = -1
DIFF_INSERT = 1
DIFF_EQUAL = 0
# see: diff_match_patch / diff_match_patch.py
DIFF_SUBS = 2


def build_style(name: str, code: int, text: str) -> str:  # noqa: C901
    if name not in name2bg.keys():
        name2bg[name] = next(
            iter(
                [
                    k
                    for k in CMDLINE_BACKGROUND_COLORS.keys()
                    if k not in name2bg.values()
                ],
            ),
        )
    if code == DIFF_INSERT:  # Insertion
        o = CMDLINE_STYLES["bold"](CMDLINE_STYLES["bg-green"](text))
    elif code == DIFF_DELETE:  # Deletion
        # o = styles["bold"](styles["striked"](styles["bg-red"](text)))
        o = CMDLINE_STYLES["bold"](CMDLINE_STYLES["bg-red"]("_" * len(text)))
    elif code == DIFF_SUBS:
        o = CMDLINE_STYLES["bold"](CMDLINE_STYLES["bg-yellow"](text))
    elif code == DIFF_EQUAL:
        o = CMDLINE_BACKGROUND_COLORS[name2bg[name]](text)
    else:
        assert False  # noqa: B011, PT015
    return o


# @dataclass
# class TranscriptCollection:
#     segment_id: str
#     transcripts: dict[str, str]
#     # TODO: remove audio_id, start, end
#     # audio_id: Optional[
#     #     str
#     # ] = None  # TODO: is this this audiocorpus_id ? and if so, why???
#     # start: Optional[Union[float, int]] = None
#     # end: Optional[float] = None
#
#     # def __post_init__(self):
#     #     if isinstance(self.start, int):
#     #         self.start = float(self.start)


@dataclass(slots=True)
class DmpCodedTextSpan:
    diff_code: int
    text: str


DmpCodedTextSpans = list[DmpCodedTextSpan]


def calc_name2code_text(
    name2text: NeDict[str, str],
    dmp,  # noqa: ANN001
    ref_name: str,
) -> NeDict[str, DmpCodedTextSpans]:
    name2code_text: dict[str, DmpCodedTextSpans] = {
        name: fix_substitution(
            [  # noqa: FURB140
                DmpCodedTextSpan(*tpl)
                for tpl in dmp.diff_main(name2text[ref_name], hyp, checklines=False)
            ],
        )
        for name, hyp in name2text.items()
        if name != ref_name
    }
    return name2code_text


def fix_substitution(  # noqa: C901,WPS231
    coded_texts: DmpCodedTextSpans,
) -> DmpCodedTextSpans:
    to_be_deleted = []
    for k, coded_text in enumerate(coded_texts):
        coded_text: DmpCodedTextSpan
        if coded_text.diff_code == DIFF_INSERT:
            is_subs = False
            if k - 1 >= 0 and coded_texts[k - 1].diff_code == DIFF_DELETE:
                is_subs = True
                to_be_deleted.append(k - 1)
            if k + 1 < len(coded_texts) and coded_texts[k + 1].diff_code == DIFF_DELETE:
                is_subs = True
                to_be_deleted.append(k + 1)
            if is_subs:
                coded_texts[k] = DmpCodedTextSpan(DIFF_SUBS, coded_text.text)

    coded_texts = [ct for k, ct in enumerate(coded_texts) if k not in to_be_deleted]
    return coded_texts  # noqa: RET504


@dataclass
class MultiDiffBlock(Buildable):
    """
    does not cache itself but is being cached by MultiDiffMatchPatchBlocks ->?
    """

    transcript_collection: list[dict[str, str]] = UNDEFINED
    hyp_diffs: Optional[dict[str, str]] = None  # noqa: UP007
    name2editdist: Optional[dict[str, float]] = None  # noqa: UP007
    dmp: Any = field(default=None, repr=False)

    def __post_init__(self):
        """
        first one is assumed to be ref!!
        """
        first = self.transcript_collection[0]
        self.ref_id, self.ref = first["service-name"], first["text"]

    def get_lines(self) -> list[str]:
        # hyp_ids = ",".join(list(self.hyp_diffs.keys()))
        hyps = list(self.hyp_diffs.values())
        # [f"{styles['bold'](self.segment_id)}"]
        return [f"ref:\t{self.ref}"] + hyps  # noqa: RUF005

    def _build_self(self) -> None:
        # name2hyp = self.transcripts
        # max_name_len = max([len("ref")] + [len(n) for n in name2hyp.keys()])
        # self.name2padded = {
        #     n: f"{n}{'_'*(max_name_len-len(n))}"
        #     for n in ["ref"] + list(name2hyp.keys())
        # }
        name2code_text = calc_name2code_text(
            {d["service-name"]: d["text"] for d in self.transcript_collection},
            self.dmp,
            self.ref_id,
        )
        # print(f"{name2code_text}")
        self.hyp_diffs = {
            f"hyp-{k}:\t{build_style(n, DIFF_EQUAL, n)}": f"hyp-{k}:\t{''.join([build_style(n, cdt.diff_code, cdt.text) for cdt in diffs])}"
            for k, (n, diffs) in enumerate(name2code_text.items())
        }

        def normalize(s):  # noqa: ANN001, ANN202
            return s.replace(" ", "")

        self.name2editdist = {
            d["service-name"]: editdistance.eval(
                normalize(self.ref),
                normalize(d["text"]),
            )
            for d in self.transcript_collection
            if d["service-name"] != self.ref_id
        }


def get_hyp(d: dict, prefix="hyp-ifinder") -> Iterator[str]:  # noqa: ANN001
    for k, v in d.items():
        if k.startswith(prefix):
            yield v


if __name__ == "__main__":
    dmp = diff_match_patch.diff_match_patch()
    a = "this is  a test"
    b = "This was a Test!"
    o = dmp.diff_main(a, b)
    print(o)  # noqa: T201

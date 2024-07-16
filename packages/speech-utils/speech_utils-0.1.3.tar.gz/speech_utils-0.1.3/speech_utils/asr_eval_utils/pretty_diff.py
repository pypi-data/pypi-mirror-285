import sys
from pathlib import Path

import icdiff
from ansi2html import Ansi2HTMLConverter
from misc_python_utils.beartypes import NeList, NeStr
from misc_python_utils.file_utils.readwrite_files import read_lines, write_file

from speech_utils.asr_eval_utils.smith_waterman_alignment import align_split


def smithwaterman_aligned_icdiffs(
    ref: NeStr,
    hyp: NeStr,
    split_len_a: int = 70,
    ref_header: str | None = "ref",
    hyp_header: str | None = "hyp",
) -> NeList[str]:
    refs, hyps = align_split(ref, hyp, split_len_a=split_len_a, debug=False)
    cd = icdiff.ConsoleDiff(cols=2 * split_len_a + 20)
    return list(cd.make_table(refs, hyps, ref_header, hyp_header))  # pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType, reportArgumentType]


def smithwaterman_aligned_icdiff(
    ref: NeStr,
    hyp: NeStr,
    split_len_a: int = 70,
    ref_header: str | None = "ref",
    hyp_header: str | None = "hyp",
) -> str:
    return "\n".join(
        smithwaterman_aligned_icdiffs(ref, hyp, split_len_a, ref_header, hyp_header),
    )


ansi2html_converter = None


def write_icdiff_to_html(file: Path, icdiff_output: str) -> None:
    global ansi2html_converter  # noqa: PLW0603
    if ansi2html_converter is None:
        ansi2html_converter = Ansi2HTMLConverter(dark_bg=False)
    diff_html = ansi2html_converter.convert(icdiff_output)
    write_file(file, diff_html)


if __name__ == "__main__":
    # ref = "NOT HAVING THE COURAGE OR THE INDUSTRY OF OUR NEIGHBOUR WHO WORKS LIKE A BUSY BEE IN THE WORLD OF MEN AND BOOKS SEARCHING WITH THE SWEAT OF HIS BROW FOR THE REAL BREAD OF LIFE WETTING THE OPEN PAGE BEFORE HIM WITH HIS TEARS PUSHING INTO THE WE HOURS OF THE NIGHT HIS QUEST ANIMATED BY THE FAIREST OF ALL LOVES THE LOVE OF TRUTH WE EASE OUR OWN INDOLENT CONSCIENCE BY CALLING HIM NAMES"
    # hyp = "NOT HAVING THE COURAGE OR THE INDUSTRY OF OUR NEIGHBOUR WHO WORKS LIKE A BUSY BEE IN THE WORLD OF MEN AN BOOKS SEARCHING WITH THE SWEAT OF HIS BROW FOR THE REAL BREAD OF LIFE WET IN THE OPEN PAGE BAFORE HIM WITH HIS TEARS PUSHING INTO THE WEE HOURS OF THE NIGHT HIS QUEST AND BY THE FAIREST OF ALL LOVES THE LOVE OF TRUTH WE EASE OUR OWN INDOLENT CONSCIENCE BY CALLING HIM NAMES"
    refs = read_lines(sys.argv[1])
    hyps = read_lines(sys.argv[2])
    for k, (ref, hyp) in enumerate(zip(refs, hyps, strict=True)):
        write_icdiff_to_html(
            Path(f"{k}.html"),
            smithwaterman_aligned_icdiff(ref, hyp),
        )

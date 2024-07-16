from misc_python_utils.beartypes import NeList

from speech_utils.audio_segmentation_utils.audio_segmentation_utils import (
    SOME_BIG_VALUE,
)
from speech_utils.audio_segmentation_utils.non_overlapping_segments_variations import (
    TextNeNoSeg,
    TTextNeNoSeg,
)
from speech_utils.data_models.timespans_with_text import TimeSpanText

#
# def expand_merge_segments_labelaware( # TODO: you want it ? you fix it!
#     start_end_labels: Annotated[
#         NeList[TimeSpanText],
#         Is[segment_starts_are_weakly_monoton_increasing],
#     ],
#     expand_by: float,
#     min_gap_dur: float,
# ) -> TextNeNoSeg:
#     """
#     used for post-clustering resegmentation
#     """
#     s_e_exp = expand_segments(
#         [(s, e) for s, e, _ in start_end_labels],
#         expand_by=expand_by,
#     )
#     return merge_segments_of_same_label(
#         TextNeNoSeg.from_segments(
#             [
#                 TimeSpanText(s, e, l)
#                 for (s, e), (_, _, l) in zip(s_e_exp, start_end_labels, strict=False)
#             ],
#         ),
#         min_gap_dur=min_gap_dur,
#     )


def merge_segments_of_same_label(
    spans: TTextNeNoSeg,
    min_gap_dur: float,
    # get_label_fun: Callable[[TimeSpanText], str] = lambda x: x.text, # TODO: make it more flexible? in case one has multiple labels/texts etc
) -> TTextNeNoSeg:
    """
    should do same as: https://github.com/NVIDIA/NeMo/blob/aff169747378bcbcec3fc224748242b36205413f/nemo/collections/asr/parts/utils/speaker_utils.py
    but "cleaner"!
    """
    groups = groups_to_merge_segments_of_same_label(spans, min_gap_dur)

    def merge_segment(first: int, last: int) -> TimeSpanText:
        return type(spans[0])(
            start=spans[first].start,
            end=spans[last].end,
            text=spans[first].text,
        )

    merged = [merge_segment(gr[0], gr[-1]) for gr in groups]
    return type(spans)(merged)


def groups_to_merge_segments_of_same_label(
    spans: TextNeNoSeg,
    min_gap_dur: float = SOME_BIG_VALUE,
    # get_label_fun:Callable[[TimeSpanText], str]=lambda x: x.text,
) -> NeList[NeList[int]]:
    """
    :param min_gap_dur: gaps (of same speaker) smaller than this get grouped
    """

    initial_group = [0]
    mergable_groupds = [initial_group]
    for k in range(len(spans) - 1):
        end = spans[k].end
        kplus1 = k + 1
        next_start = spans[kplus1].start
        is_close_enough_to_be_merged = (
            next_start - end < min_gap_dur
        )  # is relaxing "float(end) == float(next_start)", see nvidia-nemo code
        if spans[k].text == spans[kplus1].text and is_close_enough_to_be_merged:
            mergable_groupds[-1].append(kplus1)
        else:
            new_group = [kplus1]
            mergable_groupds.append(new_group)

    return mergable_groupds

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import markdown
from buildable_dataclasses.hashcached_data.hashcached_data import HashCachedData
from misc_python_utils.beartypes import NeList
from misc_python_utils.dict_utils import (
    _NOT_EXISTING,  # noqa: PLC2701
    get_dict_paths,
    get_val_from_nested_dict,
)
from misc_python_utils.file_utils.readwrite_files import write_file
from misc_python_utils.markdown_table_utils import TableHeaders, build_markdown_table
from misc_python_utils.mermaid_utils.mermaid_dag import mermaid_html_dag
from misc_python_utils.prefix_suffix import PrefixSuffix

from speech_utils.asr_eval_utils.row_col_scores import RowColScoreCollections

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class ExperimentTables(HashCachedData):
    name: str
    multiple_score_collections: Iterable[RowColScoreCollections]
    cache_base: PrefixSuffix
    precision: int = 2

    def _build_cache(self) -> None:
        (dict_key_paths, score_rows, table_headers) = calc_keypath_and_score_rows(
            row_col_scores=[
                (
                    scs.row,
                    scs.col,
                    {
                        sc.namespace: sc.scores for sc in scs.score_collections
                    },  # | {"alma-json": exp.alma_json}, # TODO: think about this alma!
                )
                for scs in self.multiple_score_collections
            ],
            row_title="service",
            col_title="corpus",
            swap=False,
        )
        svc_table = create_markdown_score_tables(
            dict_key_paths,
            score_rows,
            table_headers,
            self.precision,
        )

        print(svc_table)  # noqa: T201
        write_file(f"{self.cache_dir}/table.md", svc_table)

        html = markdown.markdown(svc_table, extensions=["markdown.extensions.tables"])
        write_file(f"{self.cache_dir}/tables.html", html)
        write_file(f"{self.cache_dir}/tables-dag.html", mermaid_html_dag(self))


def create_markdown_score_tables(
    dict_key_paths: list[list[str]],
    score_rows: list[list[dict]],
    table_headers: TableHeaders,
    precision: int = 2,
) -> str:
    tables = [
        build_table(score_rows, score_path, table_headers, precision)
        for score_path in dict_key_paths
    ]
    return "\n\n-------------------------------------------------------\n\n".join(
        [
            (
                f"### {table_headers.row_title} - {table_headers.col_title}, score-path: {'->'.join(score_path)}\n"
                f"{table}"
            )
            for table, score_path in zip(tables, dict_key_paths)  # noqa: B905
        ],
    )


def build_table(
    exp_rows: list[list[dict]],
    get_path: list[str],
    table_headers: TableHeaders,
    precision: int = 2,
) -> str:
    def format_table_cell(v: float | Any) -> str:
        if isinstance(v, float):
            v = round(v, precision)
            v = f"{v:.{precision}f}"
        if isinstance(v, _NOT_EXISTING):
            v = None
        return f"{v}"

    return build_markdown_table(
        rows=[
            [
                get_val_from_nested_dict(
                    scores,
                    get_path,
                )
                for scores in exp_row
            ]
            for exp_row in exp_rows
        ],
        table_headers=table_headers,
        format_fun=format_table_cell,
    )


def calc_keypath_and_score_rows(
    col_title: str,
    row_title: str,
    row_col_scores: NeList[tuple[str, str, dict[str, Any]]],
    swap: bool = False,
) -> tuple[list[list[str]], list[NeList[dict]], TableHeaders]:
    # dict.fromkeys instead of set, to get ordered-set
    col_names = list(dict.fromkeys([c for _r, c, _s in row_col_scores]))
    row_names = list(dict.fromkeys([r for r, _c, _s in row_col_scores]))
    if swap:
        row_title, col_title = col_title, row_title
        row_names, col_names = col_names, row_names

    def filter_fun(r, c, row_name):  # noqa: ANN001, ANN202
        if swap:
            return c == row_name
        else:  # noqa: RET505
            return r == row_name

    def filter_for_scores_in_same_row(row_name: str) -> NeList[dict]:
        return [s for r, c, s in row_col_scores if filter_fun(r, c, row_name)]

    score_rows = [filter_for_scores_in_same_row(row_name) for row_name in row_names]
    merged_dict = {}
    for row in score_rows:
        for d in row:
            merged_dict |= d
    dict_key_paths = [
        s.split(",")
        for s in sorted(
            {
                ",".join(p)
                for row in score_rows
                for cell in row
                for p in get_dict_paths(cell)
            },
        )
    ]
    headers = TableHeaders(
        row_title=row_title,
        col_title=col_title,
        row_names=row_names,
        col_names=col_names,
    )
    return dict_key_paths, score_rows, headers

r"""Contain the implementation of sections to analyze the number null
values."""

from __future__ import annotations

__all__ = [
    "NullValueSection",
    "create_section_template",
    "create_table",
    "create_table_row",
    "create_bar_figure",
]

import logging
from typing import TYPE_CHECKING

import polars as pl
from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot.utils import readable_xticklabels
from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np


logger = logging.getLogger(__name__)


class NullValueSection(BaseSection):
    r"""Implement a section that analyzes the number of null values.

    Args:
        columns: The column names.
        null_count: The number of null values for each column.
        total_count: The total number of values for each column.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.section import NullValueSection
    >>> section = NullValueSection(
    ...     columns=["col1", "col2", "col3"],
    ...     null_count=np.array([0, 1, 2]),
    ...     total_count=np.array([5, 5, 5]),
    ... )
    >>> section
    NullValueSection(
      (columns): ('col1', 'col2', 'col3')
      (null_count): array([0, 1, 2])
      (total_count): array([5, 5, 5])
      (figsize): None
    )
    >>> section.get_statistics()
    {'columns': ('col1', 'col2', 'col3'), 'null_count': (0, 1, 2), 'total_count': (5, 5, 5)}

    ```
    """

    def __init__(
        self,
        columns: Sequence[str],
        null_count: np.ndarray,
        total_count: np.ndarray,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._columns = tuple(columns)
        self._null_count = null_count.flatten().astype(int)
        self._total_count = total_count.flatten().astype(int)
        self._figsize = figsize

        if len(self._columns) != self._null_count.shape[0]:
            msg = (
                f"columns ({len(self._columns):,}) and null_count ({self._null_count.shape[0]:,}) "
                "do not match"
            )
            raise RuntimeError(msg)
        if len(self._columns) != self._total_count.shape[0]:
            msg = (
                f"columns ({len(self._columns):,}) and total_count "
                f"({self._total_count.shape[0]:,}) do not match"
            )
            raise RuntimeError(msg)

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "columns": self._columns,
                    "null_count": self._null_count,
                    "total_count": self._total_count,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def columns(self) -> tuple[str, ...]:
        r"""The columns used to compute the duplicated rows."""
        return self._columns

    @property
    def null_count(self) -> np.ndarray:
        r"""The number of null values for each column."""
        return self._null_count

    @property
    def total_count(self) -> np.ndarray:
        r"""The total number of values for each column."""
        return self._total_count

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    def get_statistics(self) -> dict:
        return {
            "columns": self._columns,
            "null_count": tuple(self._null_count.tolist()),
            "total_count": tuple(self._total_count.tolist()),
        }

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Rendering the null value distribution of all columns...")
        frame = self._get_dataframe()
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "table_alpha": self._create_table(frame=frame, sort_by="column"),
                "table_sort": self._create_table(frame=frame, sort_by="null"),
                "bar_figure": self._create_bar_figure(frame),
                "num_columns": f"{len(self._columns):,}",
                "columns": ", ".join(self._columns),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_bar_figure(self, frame: pl.DataFrame) -> str:
        frame = frame.sort(by=["null", "column"])
        fig = create_bar_figure(
            columns=frame["column"].to_list(),
            null_count=frame["null"].to_list(),
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)

    def _create_table(self, frame: pl.DataFrame, sort_by: str) -> str:
        return create_table(frame.sort(by=sort_by))

    def _get_dataframe(self) -> pl.DataFrame:
        return pl.DataFrame(
            {"column": self._columns, "null": self._null_count, "total": self._total_count},
            schema={"column": pl.String, "null": pl.Int64, "total": pl.Int64},
        )


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.null import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the number and proportion of null values for the {{num_columns}}
columns: <em>{{columns}}</em>.

<p>The columns are sorted by ascending order of number of null values in the following histogram.

{{bar_figure}}

<details>
    <summary>[show statistics per column]</summary>

    <p style="margin-top: 1rem;">
    The following tables show the number and proportion of null values for the {{num_columns}}
    columns.
    The background color of the row indicates the proportion of missing values:
    dark blues indicates more missing values than light blues.

    <div class="container-fluid">
        <div class="row align-items-start">
            <div class="col align-self-center">
                <p><b>Columns sorted by alphabetical order</b></p>

                {{table_alpha}}

            </div>
            <div class="col">
                <p><b>Columns sorted by ascending order of missing values</b></p>

                {{table_sort}}

            </div>
        </div>
    </div>
</details>

<p style="margin-top: 1rem;">
"""


def create_bar_figure(
    columns: Sequence[str],
    null_count: Sequence[int],
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return a bar figure with the distribution of null values per
    column.

    Args:
        columns: The column names.
        null_count: The number of null values for each column.
            It must have the same size as ``columns``.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> from flamme.section.null import create_bar_figure
    >>> fig = create_bar_figure(columns=["col1", "col2", "col3"], null_count=[5, 10, 2])

    ```
    """
    if len(columns) != len(null_count):
        msg = f"columns ({len(columns):,}) and null_count ({len(null_count):,}) do not match"
        raise RuntimeError(msg)
    if len(columns) == 0:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x=columns, height=null_count, color="tab:blue")
    ax.set_xlim(-0.5, len(columns) - 0.5)
    readable_xticklabels(ax, max_num_xticks=100)
    ax.set_xlabel("column")
    ax.set_ylabel("number of null values")
    ax.set_title("number of null values per column")
    return fig


def create_table(frame: pl.DataFrame) -> str:
    r"""Return a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        frame: The DataFrame to analyze.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null import create_table
    >>> frame = pl.DataFrame(
    ...     {"column": ["A", "B", "C"], "null": [0, 1, 2], "total": [4, 4, 4]},
    ...     schema={"column": pl.String, "null": pl.Int64, "total": pl.Int64},
    ... )
    >>> table = create_table(frame=frame)

    ```
    """
    rows = [
        create_table_row(column=column, null_count=null, total_count=total)
        for column, null, total in zip(
            frame["column"],
            frame["null"],
            frame["total"],
        )
    ]
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>null pct</th>
            <th>null count</th>
            <th>total count</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": "\n".join(rows)})


def create_table_row(column: str, null_count: int, total_count: int) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        null_count (int): The number of null values.
        total_count (int): The total number of rows.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from flamme.section.null import create_table_row
    >>> row = create_table_row(column="col", null_count=5, total_count=101)

    ```
    """
    pct = null_count / total_count if total_count > 0 else float("nan")
    pct_color = pct if total_count > 0 else 0
    return Template(
        """<tr>
    <th style="background-color: rgba(0, 191, 255, {{null_pct}})">{{column}}</th>
    <td {{num_style}}>{{null_pct}}</td>
    <td {{num_style}}>{{null_count}}</td>
    <td {{num_style}}>{{total_count}}</td>
</tr>"""
    ).render(
        {
            "num_style": (
                f'style="text-align: right; background-color: rgba(0, 191, 255, {pct_color})"'
            ),
            "column": column,
            "null_count": f"{null_count:,}",
            "null_pct": f"{pct:.4f}",
            "total_count": f"{total_count:,}",
        }
    )

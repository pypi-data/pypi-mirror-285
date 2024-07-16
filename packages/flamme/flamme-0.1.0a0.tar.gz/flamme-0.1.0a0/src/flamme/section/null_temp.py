r"""Contain the implementation of a section to analyze the temporal
distribution of null values for all columns."""

from __future__ import annotations

__all__ = [
    "TemporalNullValueSection",
    "create_section_template",
    "create_temporal_null_figure",
    "create_temporal_null_table",
    "create_temporal_null_table_row",
]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot import plot_null_temporal
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
from flamme.utils.null import compute_temporal_null_count

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class TemporalNullValueSection(BaseSection):
    r"""Implement a section to analyze the temporal distribution of null
    values for all columns.

    Args:
        frame: The DataFrame to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section import TemporalNullValueSection
    >>> section = TemporalNullValueSection(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col1": [None, 1.0, 0.0, 1.0],
    ...             "col2": [None, 1, 0, None],
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col1": pl.Float64,
    ...             "col2": pl.Int64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     columns=["col1", "col2"],
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )
    >>> section
    TemporalNullValueSection(
      (columns): ('col1', 'col2')
      (dt_column): datetime
      (period): 1mo
      (figsize): None
    )
    >>> section.get_statistics()
    {}

    ```
    """

    def __init__(
        self,
        frame: pl.DataFrame,
        columns: Sequence[str],
        dt_column: str,
        period: str,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        if dt_column not in frame:
            msg = (
                f"Datetime column {dt_column} is not in the DataFrame "
                f"(columns:{sorted(frame.columns)})"
            )
            raise ValueError(msg)

        self._frame = frame
        self._columns = tuple(columns)
        self._dt_column = dt_column
        self._period = period
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "columns": self._columns,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def frame(self) -> pl.DataFrame:
        r"""The DataFrame to analyze."""
        return self._frame

    @property
    def columns(self) -> tuple[str, ...]:
        r"""The columns to analyze."""
        return self._columns

    @property
    def dt_column(self) -> str:
        r"""The datetime column."""
        return self._dt_column

    @property
    def period(self) -> str:
        r"""The temporal period used to analyze the data."""
        return self._period

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(
            "Rendering the temporal distribution of null values for all columns "
            f"| datetime column: {self._dt_column} | period: {self._period}"
        )
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "dt_column": self._dt_column,
                "figure": self._create_temporal_null_figure(),
                "table": create_temporal_null_table(
                    frame=self._frame,
                    columns=self._columns,
                    dt_column=self._dt_column,
                    period=self._period,
                ),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_temporal_null_figure(self) -> str:
        fig = create_temporal_null_figure(
            frame=self._frame,
            columns=self._columns,
            dt_column=self._dt_column,
            period=self._period,
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the temporal distribution of null values in all columns.
The column <em>{{dt_column}}</em> is used as the temporal column.

{{figure}}

{{table}}
<p style="margin-top: 1rem;">
"""


def create_temporal_null_figure(
    frame: pl.DataFrame,
    columns: Sequence[str],
    dt_column: str,
    period: str,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Create a figure with the temporal null value distribution.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze.
        dt_column: The datetime column used to analyze the
            temporal distribution.
        period: The temporal period e.g. monthly or daily.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp import create_temporal_null_figure
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [None, 1.0, 0.0, 1.0],
    ...         "col2": [None, 1, 0, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Float64,
    ...         "col2": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> fig = create_temporal_null_figure(
    ...     frame=frame, columns=["col1", "col2"], dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return None
    nulls, totals, labels = compute_temporal_null_count(
        frame=frame, columns=columns, dt_column=dt_column, period=period
    )
    fig, ax = plt.subplots(figsize=figsize)
    plot_null_temporal(ax=ax, labels=labels, nulls=nulls, totals=totals)
    readable_xticklabels(ax, max_num_xticks=100)
    return fig


def create_temporal_null_table(
    frame: pl.DataFrame, columns: Sequence[str], dt_column: str, period: str
) -> str:
    r"""Create a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze.
        dt_column: The datetime column used to analyze the
            temporal distribution.
        period: The temporal period e.g. monthly or daily.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp import create_temporal_null_table_row
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [None, 1.0, 0.0, 1.0],
    ...         "col2": [None, 1, 0, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Float64,
    ...         "col2": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> table = create_temporal_null_table(
    ...     frame=frame, columns=["col1", "col2"], dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return ""
    nulls, totals, labels = compute_temporal_null_count(
        frame=frame, columns=columns, dt_column=dt_column, period=period
    )
    rows = []
    for label, null, total in zip(labels, nulls, totals):
        rows.append(create_temporal_null_table_row(label=label, num_nulls=null, total=total))
    return Template(
        """<details>
    <summary>[show statistics per temporal period]</summary>

    <p>The following table shows some statistics for each period.

    <table class="table table-hover table-responsive w-auto" >
        <thead class="thead table-group-divider">
            <tr>
                <th>period</th>
                <th>number of null values</th>
                <th>number of non-null values</th>
                <th>total number of values</th>
                <th>percentage of null values</th>
                <th>percentage of non-null values</th>
            </tr>
        </thead>
        <tbody class="tbody table-group-divider">
            {{rows}}
            <tr class="table-group-divider"></tr>
        </tbody>
    </table>
</details>
"""
    ).render({"rows": "\n".join(rows), "period": period})


def create_temporal_null_table_row(label: str, num_nulls: int, total: int) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        label: The label of the row.
        num_nulls: The number of null values.
        total: The total number of values.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp import create_temporal_null_table_row
    >>> row = create_temporal_null_table_row(label="col", num_nulls=5, total=42)

    ```
    """
    num_non_nulls = total - num_nulls
    return Template(
        """<tr>
    <th>{{label}}</th>
    <td {{num_style}}>{{num_nulls}}</td>
    <td {{num_style}}>{{num_non_nulls}}</td>
    <td {{num_style}}>{{total}}</td>
    <td {{num_style}}>{{num_nulls_pct}}</td>
    <td {{num_style}}>{{num_non_nulls_pct}}</td>
</tr>"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "label": label,
            "num_nulls": f"{num_nulls:,}",
            "num_non_nulls": f"{num_non_nulls:,}",
            "total": f"{total:,}",
            "num_nulls_pct": f"{100 * num_nulls / total:.2f}%",
            "num_non_nulls_pct": f"{100 * num_non_nulls / total:.2f}%",
        }
    )

r"""Contain the implementation of sections to analyze the number null
values for each column."""

from __future__ import annotations

__all__ = [
    "ColumnTemporalNullValueSection",
    "create_section_template",
    "create_table_section",
    "create_temporal_null_figure",
    "create_temporal_null_figures",
    "create_temporal_null_table",
    "create_temporal_null_table_row",
]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping, str_indent
from grizz.utils.imports import is_tqdm_available
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
from flamme.utils.figure import MISSING_FIGURE_MESSAGE, figure2html
from flamme.utils.null import compute_temporal_null_count

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

if is_tqdm_available():
    from tqdm import tqdm
else:  # pragma: no cover
    from grizz.utils.noop import tqdm

logger = logging.getLogger(__name__)


class ColumnTemporalNullValueSection(BaseSection):
    r"""Implement a section to analyze the temporal distribution of null
    values for all columns.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze. A plot is generated
            for each column.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        ncols: The number of columns.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section import ColumnTemporalNullValueSection
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> section = ColumnTemporalNullValueSection(
    ...     frame=frame, columns=["float", "int", "str"], dt_column="datetime", period="M"
    ... )
    >>> section
    ColumnTemporalNullValueSection(
      (columns): ('float', 'int', 'str')
      (dt_column): datetime
      (period): M
      (ncols): 2
      (figsize): (7, 5)
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
        ncols: int = 2,
        figsize: tuple[float, float] = (7, 5),
    ) -> None:
        self._frame = frame
        self._columns = tuple(columns)
        self._dt_column = dt_column
        self._period = period
        self._ncols = min(ncols, len(self._columns))
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "columns": self._columns,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "ncols": self._ncols,
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
    def ncols(self) -> int:
        r"""The number of columns to show the figures."""
        return self._ncols

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
            f"Rendering the temporal null value distribution of the following columns: "
            f"{self._columns}\ndatetime column: {self._dt_column} | period: {self._period}"
        )
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._dt_column,
                "figure": create_temporal_null_figure(
                    frame=self._frame,
                    columns=self._columns,
                    dt_column=self._dt_column,
                    period=self._period,
                    ncols=self._ncols,
                    figsize=self._figsize,
                ),
                "table": create_table_section(
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


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp_col import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the temporal distribution of null values.
The column <em>{{column}}</em> is used as the temporal column.

{{figure}}

<p style="margin-top: 1rem;">

{{table}}

<p style="margin-top: 1rem;">
"""


def create_temporal_null_figure(
    frame: pl.DataFrame,
    columns: Sequence[str],
    dt_column: str,
    period: str,
    ncols: int = 2,
    figsize: tuple[float, float] = (7, 5),
) -> str:
    r"""Create a HTML representation of a figure with the temporal null
    value distribution.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze. A plot is generated
            for each column.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        ncols: The number of columns.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Returns:
        The HTML representation of the figure.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp_col import create_temporal_null_figure
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> figures = create_temporal_null_figure(
    ...     frame=frame, columns=["float", "int", "str"], dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return MISSING_FIGURE_MESSAGE
    figures = create_temporal_null_figures(
        frame=frame, columns=columns, dt_column=dt_column, period=period, figsize=figsize
    )
    figures = add_column_to_figure(columns=columns, figures=figures)
    return Template(
        """<div class="container-fluid text-center">
  <div class="row align-items-start">
    {{columns}}
  </div>
</div>
"""
    ).render({"columns": "\n".join(split_figures_by_column(figures=figures, ncols=ncols))})


def create_temporal_null_figures(
    frame: pl.DataFrame,
    columns: Sequence[str],
    dt_column: str,
    period: str,
    figsize: tuple[float, float] = (7, 5),
) -> list[str]:
    r"""Create a HTML representation of each figure with the temporal
    null value distribution.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze. A plot is generated
            for each column.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Returns:
        The HTML representations of the figures.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp_col import create_temporal_null_figures
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> figures = create_temporal_null_figures(
    ...     frame=frame, columns=["float", "int", "str"], dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return []

    figures = []
    for column in tqdm(columns, desc="generating figures"):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(f"column: {column}")

        nulls, totals, labels = compute_temporal_null_count(
            frame=frame, columns=[column], dt_column=dt_column, period=period
        )
        plot_null_temporal(ax=ax, labels=labels, nulls=nulls, totals=totals)
        readable_xticklabels(ax, max_num_xticks=50)
        figures.append(figure2html(fig, close_fig=True))

    return figures


def add_column_to_figure(columns: Sequence[str], figures: Sequence[str]) -> list[str]:
    r"""Add the column name to the HTML representation of the figure.

    Args:
        columns: The column names.
        figures: The HTML representations of each figure.

    Returns:
        The uplated HTML representations of each figure.

    Raises:
        RuntimeError: if the number of column names is different from
            the number of figures.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp_col import add_column_to_figure
    >>> figures = add_column_to_figure(columns=["col1", "col2"], figures=["fig1", "fig2"])

    ```
    """
    if len(columns) != len(figures):
        msg = (
            f"The number of column names is different from the number of figures: "
            f"{len(columns):,} vs{len(figures):,}"
        )
        raise RuntimeError(msg)
    outputs = []
    for i, (col, figure) in enumerate(zip(columns, figures)):
        outputs.append(f'<div style="text-align:center">({i}) {col}\n{figure}</div>')
    return outputs


def split_figures_by_column(figures: Sequence[str], ncols: int) -> list[str]:
    r"""Split the figures into multiple columns.

    Args:
        figures: The HTML representations of each figure.
        ncols: The number of columns.

    Returns:
        The columns.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp_col import split_figures_by_column
    >>> cols = split_figures_by_column(figures=["fig1", "fig2", "fig3"], ncols=2)

    ```
    """
    cols = []
    for i in range(ncols):
        figs = str_indent("\n<hr>\n".join(figures[i::ncols]))
        cols.append(f'<div class="col">\n  {figs}\n</div>')
    return cols


def create_table_section(
    frame: pl.DataFrame, columns: Sequence[str], dt_column: str, period: str
) -> str:
    r"""Return a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        frame: The DataFrame to analyze.
        columns: The list of columns to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp_col import create_table_section
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> table = create_table_section(
    ...     frame=frame, columns=["float", "int", "str"], dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return ""
    tables = []
    for column in columns:
        table = create_temporal_null_table(
            frame=frame, column=column, dt_column=dt_column, period=period
        )
        tables.append(f'<p style="margin-top: 1rem;">\n\n{table}\n')
    return Template(
        """<details>
    <summary>[show statistics per temporal period]</summary>

    <p style="margin-top: 1rem;">
    The following table shows some statistics for each period of column {{column}}.

    {{tables}}
</details>
"""
    ).render({"tables": "\n".join(tables)})


def create_temporal_null_table(
    frame: pl.DataFrame, column: str, dt_column: str, period: str
) -> str:
    r"""Return a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        frame: The DataFrame to analyze.
        column: The column to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.null_temp_col import create_temporal_null_table
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> table = create_temporal_null_table(
    ...     frame=frame, column="int", dt_column="datetime", period="1mo"
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return ""
    nulls, totals, labels = compute_temporal_null_count(
        frame=frame, columns=[column], dt_column=dt_column, period=period
    )
    rows = [
        create_temporal_null_table_row(label=label, null=null, total=total)
        for label, null, total in zip(labels, nulls, totals)
    ]
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th colspan="6" style="text-align: center">column: {{column}}</th>
        </tr>
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
"""
    ).render({"rows": "\n".join(rows), "column": column, "period": period})


def create_temporal_null_table_row(label: str, null: int, total: int) -> str:
    r"""Return the HTML code of a new table row.

    Args:
        label: The label of the row.
        null: The number of null values.
        total: The total number of values.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from flamme.section.null_temp_col import create_temporal_null_table_row
    >>> row = create_temporal_null_table_row(label="col", null=5, total=42)

    ```
    """
    non_null = total - null
    return Template(
        """<tr>
    <th>{{label}}</th>
    <td {{num_style}}>{{null}}</td>
    <td {{num_style}}>{{non_null}}</td>
    <td {{num_style}}>{{total}}</td>
    <td {{num_style}}>{{nulls_pct}}</td>
    <td {{num_style}}>{{non_null_pct}}</td>
</tr>"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "label": label,
            "nulls": f"{null:,}",
            "non_null": f"{non_null:,}",
            "total": f"{total:,}",
            "nulls_pct": f"{100 * null / total:.2f}%",
            "non_null_pct": f"{100 * non_null / total:.2f}%",
        }
    )

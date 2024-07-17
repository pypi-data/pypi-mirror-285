r"""Contain the implementation of a section to analyze the temporal
distribution of a column with continuous values."""

from __future__ import annotations

__all__ = [
    "ColumnTemporalContinuousSection",
    "create_section_template",
    "create_temporal_figure",
    "create_temporal_table",
    "create_temporal_table_row",
]

import logging
from typing import TYPE_CHECKING

import numpy as np
import polars as pl
from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot import boxplot_continuous_temporal
from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html
from flamme.utils.temporal import compute_temporal_stats, to_step_names

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)


class ColumnTemporalContinuousSection(BaseSection):
    r"""Implement a section that analyzes the temporal distribution of a
    column with continuous values.

    Args:
        frame: The DataFrame to analyze.
        column: The column to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section import ColumnContinuousSection
    >>> section = ColumnTemporalContinuousSection(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    ...             "datetime": [
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=2, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col": pl.Float64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     column="col",
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )
    >>> section
    ColumnTemporalContinuousSection(
      (column): col
      (dt_column): datetime
      (period): 1mo
      (yscale): auto
      (figsize): None
    )
    >>> section.get_statistics()
    {}

    ```
    """

    def __init__(
        self,
        frame: pl.DataFrame,
        column: str,
        dt_column: str,
        period: str,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._frame = frame
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._yscale = yscale
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "column": self._column,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "yscale": self._yscale,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def column(self) -> str:
        return self._column

    @property
    def dt_column(self) -> str:
        return self._dt_column

    @property
    def yscale(self) -> str:
        return self._yscale

    @property
    def period(self) -> str:
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
            f"Rendering the temporal continuous distribution of {self._column} | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "dt_column": self._dt_column,
                "period": self._period,
                "figure": self._create_temporal_figure(),
                "table": create_temporal_table(
                    frame=self._frame,
                    column=self._column,
                    dt_column=self._dt_column,
                    period=self._period,
                ),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_temporal_figure(self) -> str:
        fig = create_temporal_figure(
            frame=self._frame,
            column=self._column,
            dt_column=self._dt_column,
            period=self._period,
            yscale=self._yscale,
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.continuous_temp import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the temporal distribution of column <em>{{column}}</em>
by using the column <em>{{dt_column}}</em>.

{{figure}}

{{table}}

<p style="margin-top: 1rem;">
"""


def create_temporal_figure(
    frame: pl.DataFrame,
    column: str,
    dt_column: str,
    period: str,
    yscale: str = "auto",
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Create a figure with the temporal value distribution.

    Args:
        frame: The DataFrame to analyze.
        column: The column to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.continuous_temp import create_temporal_figure
    >>> fig = create_temporal_figure(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    ...             "datetime": [
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=2, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col": pl.Float64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     column="col",
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return None
    groups = (
        frame.select(pl.col(dt_column).alias("datetime"), pl.col(column).alias("value"))
        .sort("datetime")
        .group_by_dynamic("datetime", every=period)
    )
    data = [np.sort(np.array(x["value"])) for _, x in groups]
    steps = to_step_names(groups=groups, period=period)
    fig, ax = plt.subplots(figsize=figsize)
    boxplot_continuous_temporal(ax=ax, data=data, steps=steps, yscale=yscale)
    return fig


def create_temporal_table(frame: pl.DataFrame, column: str, dt_column: str, period: str) -> str:
    r"""Return a HTML representation of a table with some statistics
    about the temporal value distribution.

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
    >>> from flamme.section.continuous_temp import create_temporal_table
    >>> table = create_temporal_table(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    ...             "datetime": [
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=2, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col": pl.Float64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     column="col",
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return "<span>&#9888;</span> No table is generated because the column is empty"

    stats = compute_temporal_stats(frame=frame, column=column, dt_column=dt_column, period=period)

    rows = [create_temporal_table_row(stat) for stat in stats.to_dicts()]
    return Template(
        """<details>
    <summary>[show statistics per temporal period]</summary>

    <p>The following table shows some statistics for each period of column {{column}}.

    <table class="table table-hover table-responsive w-auto" >
        <thead class="thead table-group-divider">
            <tr>
                <th>step</th>
                <th>count</th>
                <th>mean</th>
                <th>std</th>
                <th>min</th>
                <th>quantile 1%</th>
                <th>quantile 5%</th>
                <th>quantile 10%</th>
                <th>quantile 25%</th>
                <th>median</th>
                <th>quantile 75%</th>
                <th>quantile 90%</th>
                <th>quantile 95%</th>
                <th>quantile 99%</th>
                <th>max</th>
            </tr>
        </thead>
        <tbody class="tbody table-group-divider">
            {{rows}}
            <tr class="table-group-divider"></tr>
        </tbody>
    </table>
</details>
"""
    ).render({"rows": "\n".join(rows), "column": column, "period": period})


def create_temporal_table_row(stats: dict) -> str:
    r"""Return the HTML code of a new table row.

    Args:
        stats: The statistics for the row.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.continuous_temp import create_temporal_table_row
    >>> row = create_temporal_table_row(
    ...     stats={
    ...         "step": "2020-01-01",
    ...         "count": 101,
    ...         "nunique": 101,
    ...         "mean": 50.0,
    ...         "std": 29.300170647967224,
    ...         "min": 0.0,
    ...         "q01": 1.0,
    ...         "q05": 5.0,
    ...         "q10": 10.0,
    ...         "q25": 25.0,
    ...         "median": 50.0,
    ...         "q75": 75.0,
    ...         "q90": 90.0,
    ...         "q95": 95.0,
    ...         "q99": 99.0,
    ...         "max": 100.0,
    ...     }
    ... )

    ```
    """

    def to_float(value: float | None) -> float:
        if value is None:
            return float("nan")
        return value

    return Template(
        """<tr>
    <th>{{step}}</th>
    <td {{num_style}}>{{count}}</td>
    <td {{num_style}}>{{mean}}</td>
    <td {{num_style}}>{{std}}</td>
    <td {{num_style}}>{{min}}</td>
    <td {{num_style}}>{{q01}}</td>
    <td {{num_style}}>{{q05}}</td>
    <td {{num_style}}>{{q10}}</td>
    <td {{num_style}}>{{q25}}</td>
    <td {{num_style}}>{{median}}</td>
    <td {{num_style}}>{{q75}}</td>
    <td {{num_style}}>{{q90}}</td>
    <td {{num_style}}>{{q95}}</td>
    <td {{num_style}}>{{q99}}</td>
    <td {{num_style}}>{{max}}</td>
</tr>"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "step": stats["step"],
            "count": f"{stats['count']:,}",
            "mean": f"{to_float(stats['mean']):,.4f}",
            "median": f"{to_float(stats['median']):,.4f}",
            "min": f"{to_float(stats['min']):,.4f}",
            "max": f"{to_float(stats['max']):,.4f}",
            "std": f"{to_float(stats['std']):,.4f}",
            "q01": f"{to_float(stats['q01']):,.4f}",
            "q05": f"{to_float(stats['q05']):,.4f}",
            "q10": f"{to_float(stats['q10']):,.4f}",
            "q25": f"{to_float(stats['q25']):,.4f}",
            "q75": f"{to_float(stats['q75']):,.4f}",
            "q90": f"{to_float(stats['q90']):,.4f}",
            "q95": f"{to_float(stats['q95']):,.4f}",
            "q99": f"{to_float(stats['q99']):,.4f}",
        }
    )

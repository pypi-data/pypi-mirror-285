r"""Contain the implementation of a section to count the number of rows
for a given temporal window."""

from __future__ import annotations

__all__ = [
    "TemporalRowCountSection",
    "create_section_template",
    "create_temporal_count_figure",
    "create_temporal_count_table",
    "create_temporal_count_table_row",
]

import logging
from typing import TYPE_CHECKING

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
from flamme.utils.count import compute_temporal_count
from flamme.utils.figure import figure2html

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class TemporalRowCountSection(BaseSection):
    r"""Implement a section to analyze the number of rows per temporal
    window.

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
    >>> from flamme.section import TemporalRowCountSection
    >>> section = TemporalRowCountSection(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=4, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=5, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ]
    ...         },
    ...         schema={"datetime": pl.Datetime(time_unit="us", time_zone="UTC")},
    ...     ),
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )
    >>> section
    TemporalRowCountSection(dt_column=datetime, period=1mo, figsize=None)
    >>> section.get_statistics()
    {}

    ```
    """

    def __init__(
        self,
        frame: pl.DataFrame,
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
        self._dt_column = dt_column
        self._period = period
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(dt_column={self._dt_column}, period={self._period}, "
            f"figsize={self._figsize})"
        )

    @property
    def frame(self) -> pl.DataFrame:
        r"""The DataFrame to analyze."""
        return self._frame

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
            "Rendering the number of rows per temporal window "
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
                "figure": self._create_temporal_count_figure(),
                "table": create_temporal_count_table(
                    frame=self._frame,
                    dt_column=self._dt_column,
                    period=self._period,
                ),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_temporal_count_figure(self) -> str:
        fig = create_temporal_count_figure(
            frame=self._frame, dt_column=self._dt_column, period=self._period, figsize=self._figsize
        )
        return figure2html(fig, close_fig=True)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.count_rows import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the number of rows per temporal window.
The column <em>{{dt_column}}</em> is used as the temporal column.

{{figure}}

{{table}}
<p style="margin-top: 1rem;">
"""


def create_temporal_count_figure(
    frame: pl.DataFrame,
    dt_column: str,
    period: str,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return a figure with number of rows per temporal windows.

    Args:
        frame: The DataFrame to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.count_rows import create_temporal_count_figure
    >>> fig = create_temporal_count_figure(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=4, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=5, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ]
    ...         },
    ...         schema={"datetime": pl.Datetime(time_unit="us", time_zone="UTC")},
    ...     ),
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )

    ```
    """
    if frame.shape[0] == 0 or dt_column not in frame:
        return None

    counts, labels = compute_temporal_count(frame=frame, dt_column=dt_column, period=period)
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x=labels, height=counts, color="tab:blue")
    ax.set_ylabel("number of rows")
    ax.set_xlim(-0.5, len(labels) - 0.5)
    readable_xticklabels(ax, max_num_xticks=100)
    return fig


def create_temporal_count_table(frame: pl.DataFrame, dt_column: str, period: str) -> str:
    r"""Return a HTML representation of a figure with number of rows per
    temporal windows.

    Args:
        frame: The DataFrame to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.count_rows import create_temporal_count_table
    >>> table = create_temporal_count_table(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=4, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=1, day=5, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ]
    ...         },
    ...         schema={"datetime": pl.Datetime(time_unit="us", time_zone="UTC")},
    ...     ),
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )

    ```
    """
    if frame.shape[0] == 0:
        return ""
    counts, labels = compute_temporal_count(frame=frame, dt_column=dt_column, period=period)
    rows = [
        create_temporal_count_table_row(label=label, num_rows=num_rows)
        for label, num_rows in zip(labels, counts)
    ]
    return Template(
        """<details>
    <summary>[show statistics per temporal period]</summary>

    <p>The following table shows some statistics for each period.

    <table class="table table-hover table-responsive w-auto" >
        <thead class="thead table-group-divider">
            <tr>
                <th>period</th>
                <th>number of rows</th>
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


def create_temporal_count_table_row(label: str, num_rows: int) -> str:
    r"""Return the HTML code of a table row.

    Args:
        label: The label i.e. temporal window.
        num_rows: The number of rows for the given temporal
            window.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.count_rows import create_temporal_count_table_row
    >>> row = create_temporal_count_table_row(label="meow", num_rows=42)

    ```
    """
    return Template("<tr><th>{{label}}</th><td {{num_style}}>{{num_rows}}</td></tr>").render(
        {
            "num_style": 'style="text-align: right;"',
            "label": label,
            "num_rows": f"{num_rows:,}",
        }
    )

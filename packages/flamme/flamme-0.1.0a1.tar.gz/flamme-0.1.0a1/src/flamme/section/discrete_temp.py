r"""Contain the implementation of a section to analyze the temporal
distribution of a column with discrete values."""

from __future__ import annotations

__all__ = ["ColumnTemporalDiscreteSection", "create_section_template", "create_temporal_figure"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot import bar_discrete_temporal
from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.count import compute_temporal_value_counts
from flamme.utils.figure import figure2html

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class ColumnTemporalDiscreteSection(BaseSection):
    r"""Implement a section that analyzes the temporal distribution of a
    column with discrete values.

    Args:
        frame: The DataFrame to analyze.
        column: The column of the DataFrame to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.
        proportion: If ``True``, it plots the normalized number of
            occurrences for each step.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section import ColumnTemporalDiscreteSection
    >>> section = ColumnTemporalDiscreteSection(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col": [1, 42, None, 42],
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col": pl.Int64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     column="col",
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )
    >>> section
    ColumnTemporalDiscreteSection(
      (column): col
      (dt_column): datetime
      (period): 1mo
      (proportion): False
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
        proportion: bool = False,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._frame = frame
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._proportion = proportion
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "column": self._column,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "proportion": self._proportion,
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
    def period(self) -> str:
        return self._period

    @property
    def proportion(self) -> bool:
        return self._proportion

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
            f"Analyzing the temporal discrete distribution of {self._column} | "
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
            proportion=self._proportion,
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.discrete_temp import create_section_template
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
    proportion: bool = False,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Create a figure with the temporal value distribution.

    Args:
        frame: The DataFrame to analyze.
        column: The column to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.
        proportion: If ``True``, it plots the normalized number of
            occurrences for each step.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure or None if the data is empty.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.section.discrete_temp import create_temporal_figure
    >>> fig = create_temporal_figure(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col": [1, 42, None, 42],
    ...             "datetime": [
    ...                 datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...                 datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...             ],
    ...         },
    ...         schema={
    ...             "col": pl.Int64,
    ...             "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...         },
    ...     ),
    ...     column="col",
    ...     dt_column="datetime",
    ...     period="1mo",
    ... )

    ```
    """
    if frame.shape[0] == 0 or column not in frame or dt_column not in frame:
        return None

    counts, steps, values = compute_temporal_value_counts(
        frame=frame,
        column=column,
        dt_column=dt_column,
        period=period,
    )

    fig, ax = plt.subplots(figsize=figsize)
    bar_discrete_temporal(ax=ax, counts=counts, steps=steps, values=values, proportion=proportion)
    ax.set_title(f"Temporal distribution for column {column}")
    return fig

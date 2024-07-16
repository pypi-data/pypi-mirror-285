r"""Contain the implementation of a section to analyze a column with
continuous values."""

from __future__ import annotations

__all__ = [
    "ColumnContinuousSection",
    "create_section_template",
    "create_boxplot_figure",
    "create_histogram_figure",
    "create_stats_table",
]

import logging
from typing import TYPE_CHECKING

import numpy as np
from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import kurtosis, skew

from flamme.plot import boxplot_continuous, hist_continuous
from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.array import nonnan
from flamme.utils.figure import figure2html
from flamme.utils.stats import compute_statistics_continuous

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class ColumnContinuousSection(BaseSection):
    r"""Implement a section that analyzes a continuous distribution of
    values.

    Args:
        series: The series/column to analyze.
        column: The column name.
        nbins: The number of bins in the histogram.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section import ColumnContinuousSection
    >>> section = ColumnContinuousSection(
    ...     series=pl.Series([None, *list(range(101)), None]), column="col"
    ... )
    >>> section
    ColumnContinuousSection(
      (column): col
      (nbins): None
      (yscale): auto
      (xmin): None
      (xmax): None
      (figsize): None
    )
    >>> section.get_statistics()
    {'count': 103, 'nunique': 102, 'num_non_nulls': 101, 'num_nulls': 2,
     'mean': 50.0, 'std': 29.15..., 'skewness': 0.0, 'kurtosis': -1.20..., 'min': 0.0,
     'q001': 0.1, 'q01': 1.0, 'q05': 5.0, 'q10': 10.0, 'q25': 25.0, 'median': 50.0,
     'q75': 75.0, 'q90': 90.0, 'q95': 95.0, 'q99': 99.0, 'q999': 99.9, 'max': 100.0,
     '>0': 100, '<0': 0, '=0': 1}

    ```
    """

    def __init__(
        self,
        series: pl.Series,
        column: str,
        nbins: int | None = None,
        yscale: str = "auto",
        xmin: float | str | None = None,
        xmax: float | str | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._series = series
        self._column = column
        self._nbins = nbins
        self._yscale = yscale
        self._xmin = xmin
        self._xmax = xmax
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "column": self._column,
                    "nbins": self._nbins,
                    "yscale": self._yscale,
                    "xmin": self._xmin,
                    "xmax": self._xmax,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def column(self) -> str:
        return self._column

    @property
    def yscale(self) -> str:
        return self._yscale

    @property
    def nbins(self) -> int | None:
        return self._nbins

    @property
    def series(self) -> pl.Series:
        return self._series

    @property
    def xmin(self) -> float | str | None:
        return self._xmin

    @property
    def xmax(self) -> float | str | None:
        return self._xmax

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    def get_statistics(self) -> dict[str, float]:
        return compute_statistics_continuous(self._series)

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the continuous distribution of {self._column}")
        stats = self.get_statistics()
        null_values_pct = (
            f"{100 * stats['num_nulls'] / stats['count']:.2f}" if stats["count"] > 0 else "N/A"
        )
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "table": create_stats_table(stats=stats, column=self._column),
                "total_values": f"{stats['count']:,}",
                "unique_values": f"{stats['nunique']:,}",
                "null_values": f"{stats['num_nulls']:,}",
                "null_values_pct": null_values_pct,
                "histogram_figure": self._create_histogram_figure(),
                "boxplot_figure": self._create_boxplot_figure(),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_boxplot_figure(self) -> str:
        fig = create_boxplot_figure(
            series=self._series,
            xmin=self._xmin,
            xmax=self._xmax,
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)

    def _create_histogram_figure(self) -> str:
        fig = create_histogram_figure(
            series=self._series,
            column=self._column,
            nbins=self._nbins,
            yscale=self._yscale,
            xmin=self._xmin,
            xmax=self._xmax,
            figsize=self._figsize,
        )
        return figure2html(fig, close_fig=True)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.continuous import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the distribution of continuous values for column <em>{{column}}</em>.

<ul>
  <li> total values: {{total_values}} </li>
  <li> number of unique values: {{unique_values}} </li>
  <li> number of null values: {{null_values}} / {{total_values}} ({{null_values_pct}}%) </li>
</ul>

{{histogram_figure}}
{{boxplot_figure}}
{{table}}
<p style="margin-top: 1rem;">
"""


def create_boxplot_figure(
    series: pl.Series,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return a boxplot figure.

    Args:
        series: The series/column to analyze.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.continuous import create_boxplot_figure
    >>> fig = create_boxplot_figure(series=pl.Series([None, *list(range(101)), None]))

    ```
    """
    array = series.drop_nulls().to_numpy()
    if array.size == 0:
        return None
    if figsize is not None:
        figsize = (figsize[0], figsize[0] / 10)
    fig, ax = plt.subplots(figsize=figsize)
    boxplot_continuous(ax=ax, array=array, xmin=xmin, xmax=xmax)
    return fig


def create_histogram_figure(
    series: pl.Series,
    column: str,
    nbins: int | None = None,
    yscale: str = "linear",
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return a histogram figure.

    Args:
        series: The series/column to analyze.
        column: The column name.
        nbins: The number of bins in the histogram.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.continuous import create_histogram_figure
    >>> fig = create_histogram_figure(
    ...     series=pl.Series([None, *list(range(101)), None]), column="col"
    ... )

    ```
    """
    array = series.drop_nulls().to_numpy()
    if array.size == 0:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f"data distribution for column {column}")
    hist_continuous(ax=ax, array=array, nbins=nbins, xmin=xmin, xmax=xmax, yscale=yscale)

    array = nonnan(array)
    ax.legend(
        [Line2D([0], [0], linestyle="none", mfc="black", mec="none", marker="")] * 3,
        [
            f"std={np.std(array).item():.2f}",
            f"skewness={skew(array).item():.2f}",
            f"kurtosis={kurtosis(array).item():.2f}",
        ],
    )
    return fig


def create_stats_table(stats: dict, column: str) -> str:
    r"""Create the HTML code of the table with statistics.

    Args:
        stats: Specifies a dictionary with the statistics.
        column: The column name.

    Returns:
        The HTML code of the table.

    Example usage:

    ```pycon

    >>> from flamme.section.continuous import create_stats_table
    >>> table = create_stats_table(
    ...     column="col",
    ...     stats={
    ...         "count": 101,
    ...         "nunique": 101,
    ...         "num_non_nulls": 101,
    ...         "num_nulls": 0,
    ...         "mean": 50.0,
    ...         "std": 29.15,
    ...         "skewness": 0.0,
    ...         "kurtosis": -1.20,
    ...         "min": 0.0,
    ...         "q001": 0.1,
    ...         "q01": 1.0,
    ...         "q05": 5.0,
    ...         "q10": 10.0,
    ...         "q25": 25.0,
    ...         "median": 50.0,
    ...         "q75": 75.0,
    ...         "q90": 90.0,
    ...         "q95": 95.0,
    ...         "q99": 99.0,
    ...         "q999": 99.9,
    ...         "max": 100.0,
    ...         ">0": 100,
    ...         "<0": 0,
    ...         "=0": 1,
    ...     },
    ... )

    ```
    """
    return Template(
        """<details>
    <summary>[show statistics]</summary>

    <p>The following table shows some statistics about the distribution for column {{column}}.

    <table class="table table-hover table-responsive w-auto" >
        <thead class="thead table-group-divider">
            <tr><th>stat</th><th>value</th></tr>
        </thead>
        <tbody class="tbody table-group-divider">
            <tr><th>count</th><td {{num_style}}>{{count}}</td></tr>
            <tr><th>mean</th><td {{num_style}}>{{mean}}</td></tr>
            <tr><th>std</th><td {{num_style}}>{{std}}</td></tr>
            <tr><th>skewness</th><td {{num_style}}>{{skewness}}</td></tr>
            <tr><th>kurtosis</th><td {{num_style}}>{{kurtosis}}</td></tr>
            <tr><th>min</th><td {{num_style}}>{{min}}</td></tr>
            <tr><th>quantile 0.1%</th><td {{num_style}}>{{q01}}</td></tr>
            <tr><th>quantile 1%</th><td {{num_style}}>{{q01}}</td></tr>
            <tr><th>quantile 5%</th><td {{num_style}}>{{q05}}</td></tr>
            <tr><th>quantile 10%</th><td {{num_style}}>{{q10}}</td></tr>
            <tr><th>quantile 25%</th><td {{num_style}}>{{q25}}</td></tr>
            <tr><th>median</th><td {{num_style}}>{{median}}</td></tr>
            <tr><th>quantile 75%</th><td {{num_style}}>{{q75}}</td></tr>
            <tr><th>quantile 90%</th><td {{num_style}}>{{q90}}</td></tr>
            <tr><th>quantile 95%</th><td {{num_style}}>{{q95}}</td></tr>
            <tr><th>quantile 99%</th><td {{num_style}}>{{q99}}</td></tr>
            <tr><th>quantile 99.9%</th><td {{num_style}}>{{q99}}</td></tr>
            <tr><th>max</th><td {{num_style}}>{{max}}</td></tr>
            <tr><th>number of zeros</th><td {{num_style}}>{{num_zeros}}</td></tr>
            <tr><th>number of positive values</th><td {{num_style}}>{{num_pos}}</td></tr>
            <tr><th>number of negative values</th><td {{num_style}}>{{num_neg}}</td></tr>
            <tr class="table-group-divider"></tr>
        </tbody>
    </table>
</details>
"""
    ).render(
        {
            "column": column,
            "num_style": 'style="text-align: right;"',
            "count": f"{stats['count']:,}",
            "mean": f"{stats['mean']:,.4f}",
            "std": f"{stats['std']:,.4f}",
            "skewness": f"{stats['skewness']:,.4f}",
            "kurtosis": f"{stats['kurtosis']:,.4f}",
            "min": f"{stats['min']:,.4f}",
            "q001": f"{stats['q001']:,.4f}",
            "q01": f"{stats['q01']:,.4f}",
            "q05": f"{stats['q05']:,.4f}",
            "q10": f"{stats['q10']:,.4f}",
            "q25": f"{stats['q25']:,.4f}",
            "median": f"{stats['median']:,.4f}",
            "q75": f"{stats['q75']:,.4f}",
            "q90": f"{stats['q90']:,.4f}",
            "q95": f"{stats['q95']:,.4f}",
            "q99": f"{stats['q99']:,.4f}",
            "q999": f"{stats['q999']:,.4f}",
            "max": f"{stats['max']:,.4f}",
            "num_pos": f"{stats['>0']:,}",
            "num_neg": f"{stats['<0']:,}",
            "num_zeros": f"{stats['=0']:,}",
        }
    )

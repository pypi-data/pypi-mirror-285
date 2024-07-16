r"""Contain the implementation of a section to analyze the temporal
drift of a column with continuous values."""

from __future__ import annotations

__all__ = [
    "ColumnContinuousTemporalDriftSection",
    "create_section_template",
    "create_temporal_drift_figure",
]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot import hist_continuous2
from flamme.plot.utils import readable_xticklabels
from flamme.section import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import figure2html
from flamme.utils.mapping import sort_by_keys
from flamme.utils.range import find_range
from flamme.utils.temporal import to_temporal_frames

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class ColumnContinuousTemporalDriftSection(BaseSection):
    r"""Implement a section that analyzes the temporal drift of a column
    with continuous values.

    Args:
        frame: The DataFrame with the data.
        column: The column name.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        nbins: The number of bins in the histogram.
        density: If True, draw and return a probability density:
            each bin will display the bin's raw count divided by the
            total number of counts and the bin width, so that the area
            under the histogram integrates to 1.
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

    >>> from datetime import datetime, timezone
    >>> import numpy as np
    >>> import polars as pl
    >>> from flamme.section import ColumnContinuousTemporalDriftSection
    >>> rng = np.random.default_rng()
    >>> data = pl.DataFrame(
    ...     {
    ...         "col": rng.standard_normal(59),
    ...         "datetime": pl.datetime_range(
    ...             start=datetime(year=2018, month=1, day=1, tzinfo=timezone.utc),
    ...             end=datetime(year=2018, month=3, day=1, tzinfo=timezone.utc),
    ...             interval="1d",
    ...             closed="left",
    ...             eager=True,
    ...         ),
    ...     },
    ...     schema={
    ...         "col": pl.Float64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> section = ColumnContinuousTemporalDriftSection(
    ...     frame=data, column="col", dt_column="date", period="1mo"
    ... )
    >>> section
    ColumnContinuousTemporalDriftSection(
      (column): col
      (dt_column): date
      (period): 1mo
      (nbins): None
      (density): False
      (yscale): auto
      (xmin): None
      (xmax): None
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
        nbins: int | None = None,
        density: bool = False,
        yscale: str = "auto",
        xmin: float | str | None = None,
        xmax: float | str | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._frame = frame
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._nbins = nbins
        self._density = density
        self._yscale = yscale
        self._xmin = xmin
        self._xmax = xmax
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "column": self._column,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "nbins": self._nbins,
                    "density": self._density,
                    "yscale": self._yscale,
                    "xmin": self._xmin,
                    "xmax": self._xmax,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def frame(self) -> pl.DataFrame:
        return self._frame

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
    def yscale(self) -> str:
        return self._yscale

    @property
    def nbins(self) -> int | None:
        return self._nbins

    @property
    def density(self) -> bool:
        return self._density

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
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the temporal drift of {self._column}")
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "dt_column": self._dt_column,
                "temporal_drift_figure": self._create_temporal_drift_figure(),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_temporal_drift_figure(self) -> str:
        fig = create_temporal_drift_figure(
            frame=self._frame,
            column=self._column,
            dt_column=self._dt_column,
            period=self._period,
            nbins=self._nbins,
            density=self._density,
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

    >>> from flamme.section.continuous_drift import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the temporal drift of continuous values for column <em>{{column}}</em>.

{{temporal_drift_figure}}
<p style="margin-top: 1rem;">
"""


def create_temporal_drift_figure(
    frame: pl.DataFrame,
    column: str,
    dt_column: str,
    period: str,
    nbins: int | None = None,
    density: bool = False,
    yscale: str = "linear",
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return the figure to analyze the temporal drift.

    Args:
        frame: The DataFrame with the data.
        column: The column name.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        nbins: The number of bins in the histogram.
        density: If True, draw and return a probability density:
            each bin will display the bin's raw count divided by the
            total number of counts and the bin width, so that the area
            under the histogram integrates to 1.
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
        The generated figure or ``None`` if there is no valid data.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import numpy as np
    >>> import polars as pl
    >>> from flamme.section.continuous_drift import create_temporal_drift_figure
    >>> rng = np.random.default_rng()
    >>> data = pl.DataFrame(
    ...     {
    ...         "col": rng.standard_normal(59),
    ...         "datetime": pl.datetime_range(
    ...             start=datetime(year=2018, month=1, day=1, tzinfo=timezone.utc),
    ...             end=datetime(year=2018, month=3, day=1, tzinfo=timezone.utc),
    ...             interval="1d",
    ...             closed="left",
    ...             eager=True,
    ...         ),
    ...     },
    ...     schema={
    ...         "col": pl.Float64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> fig = create_temporal_drift_figure(
    ...     frame=data, column="col", dt_column="date", period="1mo"
    ... )

    ```
    """
    if column not in frame or dt_column not in frame:
        return None
    array = frame[column].drop_nulls().drop_nans().to_numpy()
    if array.size == 0:
        return None

    xmin, xmax = find_range(array, xmin=xmin, xmax=xmax)
    frames, steps = to_temporal_frames(
        frame=frame.select(column, dt_column), dt_column=dt_column, period=period
    )
    groups = sort_by_keys(dict(zip(steps, [fr[column].to_numpy() for fr in frames])))

    nrows = len(steps)
    steps1, steps2 = steps[:-1], steps[1:]
    if len(steps) == 2:
        nrows = 1
    if len(steps) > 2:
        steps1, steps2 = [steps[0], *steps1], [steps[-1], *steps2]
    if figsize is not None:
        figsize = (figsize[0], figsize[1] * nrows)
    fig, axes = plt.subplots(figsize=figsize, nrows=nrows)

    for i, (step1, step2) in enumerate(zip(steps1, steps2)):
        ax = axes[i] if nrows > 1 else axes
        hist_continuous2(
            ax=ax,
            array1=groups[step1],
            array2=groups[step2],
            label1=step1,
            label2=step2,
            xmin=xmin,
            xmax=xmax,
            nbins=nbins,
            density=density,
            yscale=yscale,
        )
        ax.set_title(f"{step1} vs {step2}")
        readable_xticklabels(ax, max_num_xticks=100)
    return fig

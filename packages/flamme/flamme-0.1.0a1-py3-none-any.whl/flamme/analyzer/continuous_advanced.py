r"""Implement continuous values analyzers."""

from __future__ import annotations

__all__ = ["ColumnContinuousAdvancedAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import ColumnContinuousAdvancedSection, EmptySection

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class ColumnContinuousAdvancedAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the temporal distribution of
    continuous values.

    Args:
        column: The column name.
        nbins: The number of bins in the histogram.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import ColumnContinuousAdvancedAnalyzer
    >>> analyzer = ColumnContinuousAdvancedAnalyzer(column="float")
    >>> analyzer
    ColumnContinuousAdvancedAnalyzer(column=float, nbins=None, yscale=auto, figsize=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "int": [None, 1, 0, 1],
    ...         "str": ["A", "B", None, None],
    ...     },
    ...     schema={"float": pl.Float64, "int": pl.Int64, "str": pl.String},
    ... )
    >>> section = analyzer.analyze(frame)

    ```
    """

    def __init__(
        self,
        column: str,
        nbins: int | None = None,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._nbins = nbins
        self._yscale = yscale
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, nbins={self._nbins}, "
            f"yscale={self._yscale}, figsize={self._figsize})"
        )

    def analyze(self, frame: pl.DataFrame) -> ColumnContinuousAdvancedSection | EmptySection:
        logger.info(f"Analyzing the continuous distribution of {self._column}")
        if self._column not in frame:
            logger.info(
                "Skipping temporal continuous distribution analysis because the column "
                f"({self._column}) is not in the DataFrame: {sorted(frame.columns)}"
            )
            return EmptySection()
        return ColumnContinuousAdvancedSection(
            column=self._column,
            series=frame[self._column],
            nbins=self._nbins,
            yscale=self._yscale,
            figsize=self._figsize,
        )

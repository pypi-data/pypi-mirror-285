r"""Implement discrete values analyzers."""

from __future__ import annotations

__all__ = ["ColumnDiscreteAnalyzer"]

import logging
from collections import Counter
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import ColumnDiscreteSection, EmptySection

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class ColumnDiscreteAnalyzer(BaseAnalyzer):
    r"""Implement a discrete distribution analyzer.

    Args:
        column: The column to analyze.
        drop_nulls: If ``True``, the NaN values are not included in the
            analysis.
        max_rows: The maximum number of rows to show in the
            table.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import ColumnDiscreteAnalyzer
    >>> analyzer = ColumnDiscreteAnalyzer(column="str")
    >>> analyzer
    ColumnDiscreteAnalyzer(column=str, drop_nulls=False, max_rows=20, yscale=auto, figsize=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...     }
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    ColumnDiscreteSection(
      (null_values): 2
      (column): str
      (yscale): auto
      (max_rows): 20
      (figsize): None
    )

    ```
    """

    def __init__(
        self,
        column: str,
        drop_nulls: bool = False,
        max_rows: int = 20,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._drop_nulls = bool(drop_nulls)
        self._max_rows = max_rows
        self._yscale = yscale
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"drop_nulls={self._drop_nulls}, max_rows={self._max_rows}, yscale={self._yscale}, "
            f"figsize={self._figsize})"
        )

    def analyze(self, frame: pl.DataFrame) -> ColumnDiscreteSection | EmptySection:
        logger.info(f"Analyzing the discrete distribution of {self._column}")
        if self._column not in frame:
            logger.info(
                f"Skipping discrete distribution analysis of column {self._column} "
                f"because it is not in the DataFrame: {sorted(frame.columns)}"
            )
            return EmptySection()
        series = frame[self._column]
        if self._drop_nulls:
            series = series.drop_nulls()
        return ColumnDiscreteSection(
            counter=Counter(series.to_list()),
            null_values=series.null_count(),
            column=self._column,
            max_rows=self._max_rows,
            yscale=self._yscale,
            figsize=self._figsize,
        )

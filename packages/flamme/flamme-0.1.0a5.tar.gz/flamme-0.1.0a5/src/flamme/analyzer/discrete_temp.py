r"""Implement discrete values analyzers."""

from __future__ import annotations

__all__ = ["ColumnTemporalDiscreteAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import ColumnTemporalDiscreteSection, EmptySection

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class ColumnTemporalDiscreteAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the temporal distribution of
    discrete values.

    Args:
        column: The column to analyze.
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.
        proportion: If ``True``, it plots the normalized number of
            occurrences for each step.
        figsize: The figure size in inches. The first dimension
            is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.analyzer import ColumnTemporalDiscreteAnalyzer
    >>> analyzer = ColumnTemporalDiscreteAnalyzer(
    ...     column="col", dt_column="datetime", period="1mo"
    ... )
    >>> analyzer
    ColumnTemporalDiscreteAnalyzer(column=col, dt_column=datetime, period=1mo, proportion=False, figsize=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col": [1, 42, None, 42],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={"col": pl.Int64, "datetime": pl.Datetime(time_unit="us", time_zone="UTC")},
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    ColumnTemporalDiscreteSection(
      (column): col
      (dt_column): datetime
      (period): 1mo
      (proportion): False
      (figsize): None
    )

    ```
    """

    def __init__(
        self,
        column: str,
        dt_column: str,
        period: str,
        proportion: bool = False,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._column = column
        self._dt_column = dt_column
        self._period = period
        self._proportion = proportion
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"dt_column={self._dt_column}, period={self._period}, "
            f"proportion={self._proportion}, figsize={self._figsize})"
        )

    def analyze(self, frame: pl.DataFrame) -> ColumnTemporalDiscreteSection | EmptySection:
        logger.info(
            f"Analyzing the temporal discrete distribution of {self._column} | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        for column in [self._column, self._dt_column]:
            if column not in frame:
                logger.info(
                    "Skipping temporal discrete distribution analysis because the column "
                    f"({column}) is not in the DataFrame"
                )
                return EmptySection()
        if self._column == self._dt_column:
            logger.info(
                "Skipping temporal discrete distribution analysis because the datetime column "
                f"({self._column}) is the column to analyze"
            )
            return EmptySection()
        return ColumnTemporalDiscreteSection(
            column=self._column,
            frame=frame,
            dt_column=self._dt_column,
            period=self._period,
            proportion=self._proportion,
            figsize=self._figsize,
        )

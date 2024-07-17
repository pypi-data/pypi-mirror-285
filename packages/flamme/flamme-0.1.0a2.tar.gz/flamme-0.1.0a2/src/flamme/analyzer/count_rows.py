r"""Implement an analyzer that generates a section about the number of
rows per temporal window."""

from __future__ import annotations

__all__ = ["TemporalRowCountAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import EmptySection, TemporalRowCountSection

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class TemporalRowCountAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the number of rows per temporal
    window.

    Args:
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.analyzer import TemporalRowCountAnalyzer
    >>> analyzer = TemporalRowCountAnalyzer(dt_column="datetime", period="1mo")
    >>> analyzer
    TemporalRowCountAnalyzer(dt_column=datetime, period=1mo, figsize=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={"datetime": pl.Datetime(time_unit="us", time_zone="UTC")},
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    TemporalRowCountSection(dt_column=datetime, period=1mo, figsize=None)

    ```
    """

    def __init__(
        self,
        dt_column: str,
        period: str,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._dt_column = dt_column
        self._period = period
        self._figsize = figsize

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(dt_column={self._dt_column}, "
            f"period={self._period}, figsize={self._figsize})"
        )

    def analyze(self, frame: pl.DataFrame) -> TemporalRowCountSection | EmptySection:
        logger.info(
            f"Analyzing the number of rows | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._dt_column not in frame:
            logger.info(
                "Skipping number of rows analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame: {sorted(frame.columns)}"
            )
            return EmptySection()
        return TemporalRowCountSection(
            frame=frame,
            dt_column=self._dt_column,
            period=self._period,
            figsize=self._figsize,
        )

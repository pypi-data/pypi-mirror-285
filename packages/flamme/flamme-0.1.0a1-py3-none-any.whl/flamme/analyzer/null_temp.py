r"""Implement an analyzer that generates a section to analyze the
temporal distribution of null values for all columns."""

from __future__ import annotations

__all__ = ["TemporalNullValueAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import EmptySection, TemporalNullValueSection

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class TemporalNullValueAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the temporal distribution of null
    values for all columns.

    Args:
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or
            daily.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.analyzer import TemporalNullValueAnalyzer
    >>> analyzer = TemporalNullValueAnalyzer(dt_column="datetime", period="M")
    >>> analyzer
    TemporalNullValueAnalyzer(
      (columns): None
      (dt_column): datetime
      (period): M
      (figsize): None
    )
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col": [None, 1, 0, 1],
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
    TemporalNullValueSection(
      (columns): ('col',)
      (dt_column): datetime
      (period): M
      (figsize): None
    )

    ```
    """

    def __init__(
        self,
        dt_column: str,
        period: str,
        columns: Sequence[str] | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._dt_column = dt_column
        self._period = period
        self._columns = columns
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "columns": self._columns,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame) -> TemporalNullValueSection | EmptySection:
        logger.info(
            f"Analyzing the temporal null value distribution | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._dt_column not in frame:
            logger.info(
                "Skipping temporal null value analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame"
            )
            return EmptySection()
        columns = sorted(frame.columns) if self._columns is None else self._columns
        if self._dt_column in columns:
            # Exclude the datetime column because it does not make sense to analyze it because
            # we cannot know the date/time if the value is null.
            columns.remove(self._dt_column)
        return TemporalNullValueSection(
            frame=frame,
            columns=columns,
            dt_column=self._dt_column,
            period=self._period,
            figsize=self._figsize,
        )

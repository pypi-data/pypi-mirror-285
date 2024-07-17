r"""Implement an analyzer that generates a section to analyze the number
of null values for each column."""

from __future__ import annotations

__all__ = ["ColumnTemporalNullValueAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import ColumnTemporalNullValueSection, EmptySection

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class ColumnTemporalNullValueAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the temporal distribution of null
    values for all columns.

    A plot is generated for each column.

    Args:
        dt_column: The datetime column used to analyze
            the temporal distribution.
        period: The temporal period e.g. monthly or daily.
        columns: The list of columns to analyze. A plot is generated
            for each column. ``None`` means all the columns.
        ncols: The number of columns.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from flamme.analyzer import ColumnTemporalNullValueAnalyzer
    >>> analyzer = ColumnTemporalNullValueAnalyzer("datetime", period="M")
    >>> analyzer
    ColumnTemporalNullValueAnalyzer(
      (columns): None
      (dt_column): datetime
      (period): M
      (ncols): 2
      (figsize): (7, 5)
    )
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [None, 1, 0, 1],
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "str": ["A", "B", None, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "int": pl.Int64,
    ...         "float": pl.Float64,
    ...         "str": pl.String,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    ColumnTemporalNullValueSection(
      (columns): ('float', 'int', 'str')
      (dt_column): datetime
      (period): M
      (ncols): 2
      (figsize): (7, 5)
    )

    ```
    """

    def __init__(
        self,
        dt_column: str,
        period: str,
        columns: Sequence[str] | None = None,
        ncols: int = 2,
        figsize: tuple[float, float] = (7, 5),
    ) -> None:
        self._dt_column = dt_column
        self._period = period
        self._columns = columns
        self._ncols = ncols
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "columns": self._columns,
                    "dt_column": self._dt_column,
                    "period": self._period,
                    "ncols": self._ncols,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame) -> ColumnTemporalNullValueSection | EmptySection:
        logger.info(
            "Analyzing the temporal null value distribution of all columns | "
            f"datetime column: {self._dt_column} | period: {self._period}"
        )
        if self._dt_column not in frame:
            logger.info(
                "Skipping monthly null value analysis because the datetime column "
                f"({self._dt_column}) is not in the DataFrame: {sorted(frame.columns)}"
            )
            return EmptySection()
        columns = sorted(frame.columns) if self._columns is None else self._columns
        if self._dt_column in columns:
            # Exclude the datetime column because it does not make sense to analyze it because
            # we cannot know the date/time if the value is null.
            columns.remove(self._dt_column)
        return ColumnTemporalNullValueSection(
            frame=frame,
            columns=columns,
            dt_column=self._dt_column,
            period=self._period,
            ncols=self._ncols,
            figsize=self._figsize,
        )

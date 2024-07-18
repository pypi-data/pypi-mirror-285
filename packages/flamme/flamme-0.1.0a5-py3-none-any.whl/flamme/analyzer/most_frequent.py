r"""Implement an analyzer that generates a section about the most
frequent values in a given columns."""

from __future__ import annotations

__all__ = ["MostFrequentValuesAnalyzer"]

import logging
from collections import Counter
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import EmptySection, MostFrequentValuesSection

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class MostFrequentValuesAnalyzer(BaseAnalyzer):
    r"""Implement a most frequent values analyzer for a given column.

    Args:
        column: The column to analyze.
        drop_nulls: If ``True``, the null values are not included in
            the analysis.
        top: The maximum number of values to show.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> import polars as pl
    >>> from flamme.analyzer import MostFrequentValuesAnalyzer
    >>> analyzer = MostFrequentValuesAnalyzer(column="col")
    >>> analyzer
    MostFrequentValuesAnalyzer(column=col, drop_nulls=False, top=100)
    >>> frame = pl.DataFrame({"col": [None, 1, 0, 1]}, schema={"col": pl.Int64})
    >>> section = analyzer.analyze(frame)
    >>> section
    MostFrequentValuesSection(
      (counter): Counter({1: 2, None: 1, 0: 1})
      (column): col
      (top): 100
      (total): 4
    )

    ```
    """

    def __init__(self, column: str, drop_nulls: bool = False, top: int = 100) -> None:
        self._column = column
        self._drop_nulls = bool(drop_nulls)
        self._top = top

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, "
            f"drop_nulls={self._drop_nulls}, top={self._top:,})"
        )

    def analyze(self, frame: pl.DataFrame) -> MostFrequentValuesSection | EmptySection:
        logger.info(f"Analyzing the most frequent values of {self._column}")
        if self._column not in frame:
            logger.info(
                f"Skipping most frequent values analysis of column {self._column} "
                f"because the column is missing"
            )
            return EmptySection()
        series = frame[self._column]
        if self._drop_nulls:
            series = series.drop_nulls()
        return MostFrequentValuesSection(
            counter=Counter(series.to_list()),
            column=self._column,
            top=self._top,
        )

r"""Implement an analyzer that generates a section to analyze the data
types of each column."""

from __future__ import annotations

__all__ = ["DataTypeAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import DataTypeSection
from flamme.utils.dtype import frame_types

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class DataTypeAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to find all the value types in each column.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import DataTypeAnalyzer
    >>> analyzer = DataTypeAnalyzer()
    >>> analyzer
    DataTypeAnalyzer()
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [42, 1, 0, 1],
    ...         "float": [1.2, 4.2, float("nan"), 2.2],
    ...         "str": ["A", "B", "C", "D"],
    ...     },
    ...     schema={"int": pl.Int64, "float": pl.Float64, "str": pl.String},
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    DataTypeSection(
      (dtypes): {'int': Int64, 'float': Float64, 'str': String}
      (types): {'int': {<class 'int'>}, 'float': {<class 'float'>}, 'str': {<class 'str'>}}
    )

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def analyze(self, frame: pl.DataFrame) -> DataTypeSection:
        logger.info("Analyzing the data types...")
        return DataTypeSection(dtypes=dict(frame.schema), types=frame_types(frame))

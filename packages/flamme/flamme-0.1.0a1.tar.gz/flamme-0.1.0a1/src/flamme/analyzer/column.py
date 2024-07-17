r"""Implement an analyzer to analyze only a subset of the columns."""

from __future__ import annotations

__all__ = ["ColumnSubsetAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping

from flamme.analyzer.base import BaseAnalyzer
from flamme.utils import setup_object

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

    from flamme.section import BaseSection

logger = logging.getLogger(__name__)


class ColumnSubsetAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to analyze only a subset of the columns.

    Args:
        columns: Soecifies the columns to select.
        analyzer: The analyzer
            or its configuration.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> import polars as pl
    >>> from flamme.analyzer import ColumnSubsetAnalyzer, NullValueAnalyzer
    >>> analyzer = ColumnSubsetAnalyzer(columns=["float", "str"], analyzer=NullValueAnalyzer())
    >>> analyzer
    ColumnSubsetAnalyzer(
      (columns): 2 ['float', 'str']
      (analyzer): NullValueAnalyzer(figsize=None)
    )
    >>> frame = pl.DataFrame(
    ...     {
    ...         "float": [1.2, 4.2, None, 2.2],
    ...         "int": [None, 1, 0, 1],
    ...         "str": ["A", "B", None, None],
    ...     },
    ...     schema={"float": pl.Float64, "int": pl.Int64, "str": pl.String},
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    NullValueSection(
      (columns): ('float', 'str')
      (null_count): array([1, 2])
      (total_count): array([4, 4])
      (figsize): None
    )

    ```
    """

    def __init__(self, columns: Sequence[str], analyzer: BaseAnalyzer | dict) -> None:
        self._columns = list(columns)
        self._analyzer = setup_object(analyzer)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {"columns": f"{len(self._columns)} {self._columns}", "analyzer": self._analyzer}
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame) -> BaseSection:
        logger.info(f"Selecting {len(self._columns):,} columns: {self._columns}")
        return self._analyzer.analyze(frame.select(self._columns))

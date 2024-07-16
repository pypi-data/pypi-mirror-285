r"""Implement an analyzer that generates a section to analyze number of
duplicated rows."""

from __future__ import annotations

__all__ = ["DuplicatedRowAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import DuplicatedRowSection

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class DuplicatedRowAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to show the number of duplicated rows.

    Args:
        columns: The columns used to compute the duplicated
            rows. ``None`` means all the columns.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import DuplicatedRowAnalyzer
    >>> analyzer = DuplicatedRowAnalyzer()
    >>> analyzer
    DuplicatedRowAnalyzer(columns=None, figsize=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.2, 4.2, 4.2, 2.2],
    ...         "col2": [1, 1, 1, 1],
    ...         "col3": [1, 2, 2, 2],
    ...     },
    ...     schema={"col1": pl.Float64, "col2": pl.Int64, "col3": pl.Int64},
    ... )
    >>> section = analyzer.analyze(frame)
    >>> section
    DuplicatedRowSection(
      (frame): (4, 3)
      (columns): None
      (figsize): None
    )

    ```
    """

    def __init__(
        self,
        columns: Sequence[str] | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._columns = columns
        self._figsize = figsize

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(columns={self._columns}, figsize={self._figsize})"

    def analyze(self, frame: pl.DataFrame) -> DuplicatedRowSection:
        logger.info(f"Analyzing the duplicated rows section using the columns: {self._columns}")
        return DuplicatedRowSection(frame=frame, columns=self._columns, figsize=self._figsize)

r"""Implement an analyzer to analyze only a subset of the columns."""

from __future__ import annotations

__all__ = ["ContentAnalyzer"]

import logging
from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import ContentSection

if TYPE_CHECKING:
    import polars as pl

    from flamme.section import BaseSection

logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer that generates the given custom content.

    Args:
        content: The content to use in the HTML code.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import ContentAnalyzer
    >>> analyzer = ContentAnalyzer(content="meow")
    >>> analyzer
    ContentAnalyzer()
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
    ContentSection()

    ```
    """

    def __init__(self, content: str) -> None:
        self._content = str(content)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def analyze(self, frame: pl.DataFrame) -> BaseSection:  # noqa: ARG002
        logger.info("Generating the given custom content...")
        return ContentSection(content=self._content)

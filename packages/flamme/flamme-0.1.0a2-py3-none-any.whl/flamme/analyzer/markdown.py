r"""Implement an analyzer that generates a markdown section."""

from __future__ import annotations

__all__ = ["MarkdownAnalyzer"]

from typing import TYPE_CHECKING

from flamme.analyzer.base import BaseAnalyzer
from flamme.section import MarkdownSection
from flamme.utils.imports import check_markdown

if TYPE_CHECKING:
    import polars as pl


class MarkdownAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer that adds a mardown string to the report.

    Args:
        desc: The markdown description.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import MarkdownAnalyzer
    >>> analyzer = MarkdownAnalyzer(desc="hello cats!")
    >>> analyzer
    MarkdownAnalyzer()
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
    MarkdownSection()

    ```
    """

    def __init__(self, desc: str) -> None:
        check_markdown()
        self._desc = str(desc)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def analyze(self, frame: pl.DataFrame) -> MarkdownSection:  # noqa: ARG002
        return MarkdownSection(desc=self._desc)

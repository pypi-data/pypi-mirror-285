r"""Implement an analyzer to automatically selects an analyzer based on
a given selection logic."""

from __future__ import annotations

__all__ = ["ChoiceAnalyzer", "NumUniqueSelection"]

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer

if TYPE_CHECKING:

    import polars as pl

    from flamme.section import BaseSection


class ChoiceAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer to analyze multiple analyzers.

    Args:
        analyzers: The mappings to analyze. The key of each analyzer
            is used to organize the metrics and report.
        selection_fn: Specifies a callable with the selection logic.
            The callable returns the key of the analyzer to use based
            on the data in the input DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import (
    ...     ChoiceAnalyzer,
    ...     NullValueAnalyzer,
    ...     DuplicatedRowAnalyzer,
    ... )
    >>> analyzer = ChoiceAnalyzer(
    ...     {"null": NullValueAnalyzer(), "duplicate": DuplicatedRowAnalyzer()},
    ...     selection_fn=lambda frame: (
    ...         "null" if frame.null_count().pipe(sum).item() > 0 else "duplicate"
    ...     ),
    ... )
    >>> analyzer
    ChoiceAnalyzer(
      (null): NullValueAnalyzer(figsize=None)
      (duplicate): DuplicatedRowAnalyzer(columns=None, figsize=None)
    )
    >>> frame = pl.DataFrame(
    ...     {
    ...         "float": [1.2, 4.2, 1.2, 2.2],
    ...         "int": [42, 1, 0, 1],
    ...         "str": ["A", "B", "C", "D"],
    ...     },
    ...     schema={"float": pl.Float64, "int": pl.Int64, "str": pl.String},
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
        analyzers: Mapping[str, BaseAnalyzer | dict],
        selection_fn: Callable[[pl.DataFrame], str],
    ) -> None:
        self._analyzers = {name: setup_analyzer(analyzer) for name, analyzer in analyzers.items()}
        self._selection_fn = selection_fn

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  {str_indent(str_mapping(self._analyzers))}\n)"

    @property
    def analyzers(self) -> dict[str, BaseAnalyzer]:
        return self._analyzers

    def analyze(self, frame: pl.DataFrame) -> BaseSection:
        analyzer = self._analyzers[self._selection_fn(frame)]
        return analyzer.analyze(frame)


class NumUniqueSelection(Callable):
    r"""Implement a selection logic based on the number of unique values
    in a column.

    Args:
        column: The column to check.
        threshold: The threshold of number of unique values.
        small: The string to return if the number of unique
            values is lower than the threshold.
        large: The string to return if the number of unique
            values is greater than the threshold.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> import polars as pl
    >>> from flamme.analyzer.choice import NumUniqueSelection
    >>> selection = NumUniqueSelection(column="col")
    >>> selection
    NumUniqueSelection(column=col, threshold=100, small=small, large=large)
    >>> selection(pl.DataFrame({"col": np.arange(10)}))
    small
    >>> selection(pl.DataFrame({"col": np.arange(1000)}))
    large

    ```
    """

    def __init__(
        self, column: str, threshold: int = 100, small: str = "small", large: str = "large"
    ) -> None:
        self._column = column
        self._threshold = threshold
        self._small = small
        self._large = large

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(column={self._column}, threshold={self._threshold}, "
            f"small={self._small}, large={self._large})"
        )

    def __call__(self, frame: pl.DataFrame) -> str:
        nunique = frame[self._column].n_unique()
        return self._small if nunique <= self._threshold else self._large

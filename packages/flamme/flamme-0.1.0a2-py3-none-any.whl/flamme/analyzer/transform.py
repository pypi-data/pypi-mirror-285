r"""Implement an analyzer that transforms the data before to analyze the
data."""

from __future__ import annotations

__all__ = ["TransformAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping
from grizz.transformer import BaseTransformer, setup_transformer

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer

if TYPE_CHECKING:
    import polars as pl

    from flamme.section import BaseSection

logger = logging.getLogger(__name__)


class TransformAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer that filters the data before to analyze the
    data.

    Args:
        transformer: Soecifies the transformer.
        analyzer: The analyzer or its configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.analyzer import TransformAnalyzer, NullValueAnalyzer
    >>> from grizz.transformer import SqlTransformer
    >>> analyzer = TransformAnalyzer(
    ...     transformer=SqlTransformer("SELECT * FROM self WHERE float > 1"),
    ...     analyzer=NullValueAnalyzer(),
    ... )
    >>> analyzer
    TransformAnalyzer(
      (transformer): SqlTransformer(
          (query): SELECT * FROM self WHERE float > 1
        )
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
      (columns): ('float', 'int', 'str')
      (null_count): array([0, 1, 1])
      (total_count): array([3, 3, 3])
      (figsize): None
    )

    ```
    """

    def __init__(self, transformer: BaseTransformer | dict, analyzer: BaseAnalyzer | dict) -> None:
        self._transformer = setup_transformer(transformer)
        self._analyzer = setup_analyzer(analyzer)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping({"transformer": self._transformer, "analyzer": self._analyzer})
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame) -> BaseSection:
        logger.info("Transforming the DataFrame...")
        frame = self._transformer.transform(frame)
        return self._analyzer.analyze(frame)

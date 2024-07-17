r"""Contain the implementation of a simple reporter."""

from __future__ import annotations

__all__ = ["Reporter"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping
from coola.utils.path import sanitize_path
from grizz.ingestor import BaseIngestor, setup_ingestor
from grizz.transformer import BaseTransformer, setup_transformer
from iden.io import save_text

from flamme.analyzer.base import BaseAnalyzer, setup_analyzer
from flamme.reporter.base import BaseReporter
from flamme.reporter.utils import create_html_report

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class Reporter(BaseReporter):
    r"""Implement a simple reporter.

    Args:
        ingestor: The ingestor or its configuration.
        transformer: The data transformer or its configuration.
        ingestor: The analyzer or its configuration.
        report_path: The path where to save the HTML report.
        max_toc_depth: The maximum level to show in the
            table of content.

    Example usage:

    ```pycon

    >>> from flamme.analyzer import NullValueAnalyzer
    >>> from grizz.ingestor import ParquetIngestor
    >>> from grizz.transformer import SequentialTransformer
    >>> from flamme.reporter import Reporter
    >>> reporter = Reporter(
    ...     ingestor=ParquetIngestor("/path/to/data.parquet"),
    ...     transformer=SequentialTransformer(transformers=[]),
    ...     analyzer=NullValueAnalyzer(),
    ...     report_path="/path/to/report.html",
    ... )
    >>> report = reporter.compute()  # doctest: +SKIP

    ```
    """

    def __init__(
        self,
        ingestor: BaseIngestor | dict,
        transformer: BaseTransformer | dict,
        analyzer: BaseAnalyzer | dict,
        report_path: Path | str,
        max_toc_depth: int = 6,
    ) -> None:
        self._ingestor = setup_ingestor(ingestor)
        logger.info(f"ingestor:\n{ingestor}")
        self._transformer = setup_transformer(transformer)
        logger.info(f"transformer:\n{transformer}")
        self._analyzer = setup_analyzer(analyzer)
        logger.info(f"analyzer:\n{analyzer}")
        self._report_path = sanitize_path(report_path)
        self._max_toc_depth = int(max_toc_depth)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "ingestor": self._ingestor,
                    "transformer": self._transformer,
                    "analyzer": self._analyzer,
                    "report_path": self._report_path,
                    "max_toc_depth": self._max_toc_depth,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> None:
        logger.info("Ingesting the DataFrame...")
        frame = self._ingestor.ingest()
        logger.info(f"Transforming the DataFrame {frame.shape}...")
        frame = self._transformer.transform(frame)
        logger.info(f"Analyzing the DataFrame {frame.shape}...")
        section = self._analyzer.analyze(frame)
        logger.info("Creating the HTML report...")
        report = create_html_report(
            toc=section.render_html_toc(max_depth=self._max_toc_depth),
            body=section.render_html_body(),
        )
        logger.info(f"Saving HTML report at {self._report_path}...")
        save_text(report, self._report_path, exist_ok=True)

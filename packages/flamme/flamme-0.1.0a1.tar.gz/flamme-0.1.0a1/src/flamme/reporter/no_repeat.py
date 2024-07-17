r"""Contain a wrapper around a reporter to generate the report only
once."""

from __future__ import annotations

__all__ = ["NoRepeatReporter"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping
from coola.utils.path import sanitize_path

from flamme.reporter.base import BaseReporter, setup_reporter

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class NoRepeatReporter(BaseReporter):
    r"""Implement a reporter that computes the report only once.

    Args:
        reporter: The reporter or its configuration.
        report_path: The path where to save the HTML report.

    Example usage:

    ```pycon

    >>> from flamme.analyzer import NullValueAnalyzer
    >>> from grizz.ingestor import ParquetIngestor
    >>> from grizz.transformer import SequentialTransformer
    >>> from flamme.reporter import Reporter, NoRepeatReporter
    >>> reporter = NoRepeatReporter(
    ...     reporter=Reporter(
    ...         ingestor=ParquetIngestor("/path/to/data.parquet"),
    ...         transformer=SequentialTransformer(transformers=[]),
    ...         analyzer=NullValueAnalyzer(),
    ...         report_path="/path/to/report.html",
    ...     ),
    ...     report_path="/path/to/report.html",
    ... )
    >>> report = reporter.compute()  # doctest: +SKIP

    ```
    """

    def __init__(
        self,
        reporter: BaseReporter | dict,
        report_path: Path | str,
    ) -> None:
        self._reporter = setup_reporter(reporter)
        self._report_path = sanitize_path(report_path)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "reporter": self._reporter,
                    "report_path": self._report_path,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> None:
        if self._report_path.is_file():
            logger.warning(
                f"The report ({self._report_path}) already exists and it is not re-computed"
            )
            return
        self._reporter.compute()

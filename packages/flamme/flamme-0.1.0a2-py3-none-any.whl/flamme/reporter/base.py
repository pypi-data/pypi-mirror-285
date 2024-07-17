r"""Contain the base class to implement a reporter."""

from __future__ import annotations

__all__ = ["BaseReporter", "is_reporter_config", "setup_reporter"]

import logging
from abc import ABC

from objectory import AbstractFactory
from objectory.utils import is_object_config

logger = logging.getLogger(__name__)


class BaseReporter(ABC, metaclass=AbstractFactory):
    r"""Define the base class to compute a HTML report.

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
    >>> reporter
    Reporter(
      (ingestor): ParquetIngestor(path=/path/to/data.parquet)
      (transformer): SequentialTransformer()
      (analyzer): NullValueAnalyzer(figsize=None)
      (report_path): /path/to/report.html
      (max_toc_depth): 6
    )
    >>> report = reporter.compute()  # doctest: +SKIP

    ```
    """

    def compute(self) -> None:
        r"""Generate a HTML report.

        Example usage:

        ```pycon

        >>> from flamme.analyzer import NullValueAnalyzer
        >>> from grizz.ingestor import ParquetIngestor
        >>> from grizz.transformer import SequentialTransformer
        >>> from flamme.reporter import Reporter
        >>> reporter = Reporter(
        ...     ingestor=ParquetIngestor("/path/to/data.parquet"),
        ...     transformer=SequentialTransformer(transformers=[]),
        ...     analyzer=NullValueAnalyzer(figsize=None),
        ...     report_path="/path/to/report.html",
        ... )
        >>> report = reporter.compute()  # doctest: +SKIP

        ```
        """


def is_reporter_config(config: dict) -> bool:
    r"""Indicate if the input configuration is a configuration for a
    ``BaseReporter``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config: The configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseReporter`` object.

    Example usage:

    ```pycon

    >>> from flamme.reporter import is_reporter_config
    >>> is_reporter_config(
    ...     {
    ...         "_target_": "flamme.reporter.Reporter",
    ...         "ingestor": {
    ...             "_target_": "grizz.ingestor.CsvIngestor",
    ...             "path": "/path/to/data.csv",
    ...         },
    ...         "transformer": {"_target_": "grizz.transformer.DropDuplicate"},
    ...         "analyzer": {"_target_": "flamme.analyzer.NullValueAnalyzer"},
    ...         "report_path": "/path/to/report.html",
    ...     }
    ... )
    True

    ```
    """
    return is_object_config(config, BaseReporter)


def setup_reporter(
    reporter: BaseReporter | dict,
) -> BaseReporter:
    r"""Set up a reporter.

    The reporter is instantiated from its configuration
    by using the ``BaseReporter`` factory function.

    Args:
        reporter: Specifies an reporter or its configuration.

    Returns:
        An instantiated reporter.

    Example usage:

    ```pycon

    >>> from flamme.reporter import setup_reporter
    >>> reporter = setup_reporter(
    ...     {
    ...         "_target_": "flamme.reporter.Reporter",
    ...         "ingestor": {
    ...             "_target_": "grizz.ingestor.CsvIngestor",
    ...             "path": "/path/to/data.csv",
    ...         },
    ...         "transformer": {"_target_": "grizz.transformer.DropDuplicate"},
    ...         "analyzer": {"_target_": "flamme.analyzer.NullValueAnalyzer"},
    ...         "report_path": "/path/to/report.html",
    ...     }
    ... )
    >>> reporter
    Reporter(
      (ingestor): CsvIngestor(path=/path/to/data.csv)
      (transformer): DropDuplicateTransformer(columns=None, ignore_missing=False)
      (analyzer): NullValueAnalyzer(figsize=None)
      (report_path): /path/to/report.html
      (max_toc_depth): 6
    )

    ```
    """
    if isinstance(reporter, dict):
        logger.info("Initializing an reporter from its configuration... ")
        reporter = BaseReporter.factory(**reporter)
    if not isinstance(reporter, BaseReporter):
        logger.warning(f"reporter is not a `BaseReporter` (received: {type(reporter)})")
    return reporter

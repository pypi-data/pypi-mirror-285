r"""Contain the implementation of a parquet schema reader."""

from __future__ import annotations

__all__ = ["ParquetSchemaReader"]

import logging
from typing import TYPE_CHECKING

from coola.utils.path import sanitize_path
from pyarrow.parquet import read_schema

from flamme.schema.reader.base import BaseSchemaReader

if TYPE_CHECKING:
    from pathlib import Path

    import pyarrow as pa

logger = logging.getLogger(__name__)


class ParquetSchemaReader(BaseSchemaReader):
    r"""Implement a parquet schema reader.

    Args:
        path: The path to the parquet file to ingest.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> import polars as pl
    >>> from flamme.schema.reader import ParquetSchemaReader
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = Path(tmpdir).joinpath("data.parquet")
    ...     pl.DataFrame(
    ...         {
    ...             "col1": [1, 2, 3, 4, 5],
    ...             "col2": ["a", "b", "c", "d", "e"],
    ...             "col3": [1.2, 2.2, 3.2, 4.2, 5.2],
    ...         }
    ...     ).write_parquet(path)
    ...     reader = ParquetSchemaReader(path)
    ...     reader
    ...     schema = reader.read()
    ...     schema
    ...
    ParquetSchemaReader(path=.../data.parquet)
    col1: int64
    col2: large_string
    col3: double

    ```
    """

    def __init__(self, path: Path | str) -> None:
        self._path = sanitize_path(path)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(path={self._path})"

    def read(self) -> pa.Schema:
        logger.info(f"reading the schema from parquet file {self._path}...")
        schema = read_schema(self._path)
        logger.info("schema read")
        return schema

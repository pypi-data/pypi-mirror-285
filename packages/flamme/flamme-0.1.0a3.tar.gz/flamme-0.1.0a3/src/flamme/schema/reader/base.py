r"""Contain the base class to implement an reader."""

from __future__ import annotations

__all__ = ["BaseSchemaReader", "is_schema_reader_config", "setup_schema_reader"]

import logging
from abc import ABC
from typing import TYPE_CHECKING

from objectory import AbstractFactory
from objectory.utils import is_object_config

if TYPE_CHECKING:
    import pyarrow as pa

logger = logging.getLogger(__name__)


class BaseSchemaReader(ABC, metaclass=AbstractFactory):
    r"""Define the base class to implement a schema reader.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> import polars as pl
    >>> from pathlib import Path
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

    def read(self) -> pa.Schema:
        r"""Read the schema associated to a DataFrame.

        Returns:
            The ingested DataFrame.

        Example usage:

        ```pycon

        >>> import tempfile
        >>> import polars as pl
        >>> from pathlib import Path
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
        ...     schema = reader.read()
        ...     schema
        ...
        col1: int64
        col2: large_string
        col3: double

        ```
        """


def is_schema_reader_config(config: dict) -> bool:
    r"""Indicate if the input configuration is a configuration for a
    ``BaseSchemaReader``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config: The configuration to check.

    Returns:
        ``True`` if the input configuration is a configuration
            for a ``BaseSchemaReader`` object.

    Example usage:

    ```pycon

    >>> from flamme.schema.reader import is_schema_reader_config
    >>> is_schema_reader_config(
    ...     {
    ...         "_target_": "flamme.schema.reader.ParquetSchemaReader",
    ...         "path": "/path/to/data.parquet",
    ...     }
    ... )
    True

    ```
    """
    return is_object_config(config, BaseSchemaReader)


def setup_schema_reader(
    reader: BaseSchemaReader | dict,
) -> BaseSchemaReader:
    r"""Set up a schema reader.

    The reader is instantiated from its configuration
    by using the ``BaseSchemaReader`` factory function.

    Args:
        reader: Specifies a schema reader or its configuration.

    Returns:
        An instantiated schema reader.

    Example usage:

    ```pycon

    >>> from flamme.schema.reader import setup_schema_reader
    >>> reader = setup_schema_reader(
    ...     {
    ...         "_target_": "flamme.schema.reader.ParquetSchemaReader",
    ...         "path": "/path/to/data.parquet",
    ...     }
    ... )
    >>> reader
    ParquetSchemaReader(path=.../data.parquet)

    ```
    """
    if isinstance(reader, dict):
        logger.info("Initializing a schema reader from its configuration... ")
        reader = BaseSchemaReader.factory(**reader)
    if not isinstance(reader, BaseSchemaReader):
        logger.warning(f"reader is not a `BaseSchemaReader` (received: {type(reader)})")
    return reader

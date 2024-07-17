r"""Contain the implementation of a simple ingestor."""

from __future__ import annotations

__all__ = ["SchemaReader"]

from typing import TYPE_CHECKING

from flamme.schema.reader.base import BaseSchemaReader

if TYPE_CHECKING:
    import polars as pl
    import pyarrow as pa


class SchemaReader(BaseSchemaReader):
    r"""Implement a simple DataFrame ingestor.

    Args:
        frame: The DataFrame to ingest.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.schema.reader import SchemaReader
    >>> reader = SchemaReader(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col1": [1, 2, 3, 4, 5],
    ...             "col2": [1.1, 2.2, 3.3, 4.4, 5.5],
    ...             "col4": ["a", "b", "c", "d", "e"],
    ...         },
    ...         schema={"col1": pl.Int64, "col2": pl.Float64, "col4": pl.String},
    ...     )
    ... )
    >>> reader
    SchemaReader(shape=(5, 3))
    >>> schema = reader.read()
    >>> schema
    col1: int64
    col2: double
    col4: large_string
    ...

    ```
    """

    def __init__(self, frame: pl.DataFrame) -> None:
        self._frame = frame.to_arrow()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(shape={self._frame.shape})"

    def read(self) -> pa.Schema:
        return self._frame.schema

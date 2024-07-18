r"""Contain utility functions to filter columns in DataFrames."""

from __future__ import annotations

__all__ = [
    "find_columns_decimal",
    "find_columns_str",
    "find_columns_type",
]

from decimal import Decimal
from typing import TYPE_CHECKING

from flamme.utils.dtype import frame_types

if TYPE_CHECKING:
    import polars as pl


def find_columns_type(frame: pl.DataFrame, cls: type) -> tuple[str, ...]:
    r"""Find the list of columns that contains a given type.

    Args:
        frame: The DataFrame to filter.
        cls: The type to find.

    Returns:
        tuple: The tuple of columns with the given type.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.filtering import find_columns_type
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1, 2, 3, 4, 5],
    ...         "col2": ["1", "2", "3", "4", "5"],
    ...         "col3": ["1", "2", "3", "4", "5"],
    ...         "col4": ["a", "b", "c", "d", "e"],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.String,
    ...         "col3": pl.String,
    ...         "col4": pl.String,
    ...     },
    ... )
    >>> find_columns_type(frame, str)
    ('col2', 'col3', 'col4')

    ```
    """
    types = frame_types(frame)
    return tuple(col for col, tps in types.items() if cls in tps)


def find_columns_decimal(frame: pl.DataFrame) -> tuple[str, ...]:
    r"""Find the list of columns that contains the type string.

    Args:
        frame: The DataFrame.

    Returns:
        The tuple of columns with the type string.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from decimal import Decimal
    >>> from flamme.utils.filtering import find_columns_decimal
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1, 2, 3, 4, 5],
    ...         "col2": [1.0, 2.0, 3.0, 4.0, 5.0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0],
    ...         "col4": ["a", "b", "c", "d", "e"],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.Float64,
    ...         "col3": pl.Decimal,
    ...         "col4": pl.String,
    ...     },
    ... )
    >>> find_columns_decimal(frame)
    ('col3',)

    ```
    """
    return find_columns_type(frame, Decimal)


def find_columns_str(frame: pl.DataFrame) -> tuple[str, ...]:
    r"""Find the list of columns that contains the type string.

    Args:
        frame: The input DataFrame.

    Returns:
        The tuple of columns with the type string.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.filtering import find_columns_str
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1, 2, 3, 4, 5],
    ...         "col2": ["1", "2", "3", "4", "5"],
    ...         "col3": ["1", "2", "3", "4", "5"],
    ...         "col4": ["a", "b", "c", "d", "e"],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.String,
    ...         "col3": pl.String,
    ...         "col4": pl.String,
    ...     },
    ... )
    >>> find_columns_str(frame)
    ('col2', 'col3', 'col4')

    ```
    """
    return find_columns_type(frame, str)

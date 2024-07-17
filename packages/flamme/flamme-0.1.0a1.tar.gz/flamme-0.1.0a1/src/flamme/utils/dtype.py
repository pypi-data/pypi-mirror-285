r"""Contain utility functions to manage data types."""

from __future__ import annotations

__all__ = [
    "frame_types",
    "series_types",
]

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


def frame_types(frame: pl.DataFrame) -> dict[str, set[type]]:
    r"""Return the value types per column.

    Args:
        frame: The DataFrame to analyze.

    Returns:
        A dictionary with the value types for each column.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.dtype import frame_types
    >>> frame = pl.DataFrame(
    ...     {
    ...         "int": [2, 1, 0, 1],
    ...         "float": [1.2, 4.2, float("nan"), 2.2],
    ...     },
    ...     schema={"int": pl.Int64, "float": pl.Float64},
    ... )
    >>> types = frame_types(frame)
    >>> types
    {'int': {<class 'int'>}, 'float': {<class 'float'>}}

    ```
    """
    return {col: series_types(frame[col]) for col in frame.columns}


def series_types(series: pl.Series) -> set[type]:
    r"""Return the value types in a ``polars.Series``.

    Args:
        series: The DataFrame to analyze.

    Returns:
        A dictionary with the value types for each column.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.dtype import series_types
    >>> coltypes = series_types(pl.Series([1.2, 4.2, float("nan"), 2.2]))
    >>> coltypes
    {<class 'float'>}

    ```
    """
    return {type(x) for x in series.to_list()}


TYPE_NAMES = {}


def compact_type_name(typ: type) -> str:
    r"""Return a compact type name when possible.

    Args:
        typ: The input type.

    Returns:
        The compact type name.

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.dtype import compact_type_name
    >>> name = compact_type_name(int)
    >>> name
    int

    ```
    """
    name = str(typ).split("'", maxsplit=2)[1].rsplit("'", maxsplit=2)[0]
    return TYPE_NAMES.get(name, name)

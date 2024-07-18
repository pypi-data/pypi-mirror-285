r"""Contain utility functions to generate data in a temporal range."""

from __future__ import annotations

__all__ = ["datetime_range"]


from typing import TYPE_CHECKING, Any

import polars as pl
from grizz.utils.datetime import find_end_datetime

if TYPE_CHECKING:
    from datetime import date, datetime, timedelta

    from polars._typing import IntoExprColumn


def datetime_range(
    start: datetime | date | IntoExprColumn,
    periods: int,
    interval: str | timedelta = "1d",
    **kwargs: Any,
) -> pl.Series | pl.Expr:
    r"""Generate a datetime range.

    Args:
        start: The lower bound of the datetime range.
        interval: The interval of the range periods, specified as a
            Python timedelta object or using the Polars duration
            string language.
        periods: The number of periods after the start.
        **kwargs: Keyword arguments passed to ``polars.datetime_range``

    Returns:
        Column of data type ``Datetime``.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> from flamme.utils.data import datetime_range
    >>> series = datetime_range(
    ...     start=datetime(
    ...         year=2017, month=2, day=3, hour=4, minute=5, second=6, tzinfo=timezone.utc
    ...     ),
    ...     periods=5,
    ...     interval="1d",
    ...     eager=True,
    ... ).alias("datetime")
    >>> series
    shape: (5,)
    Series: 'datetime' [datetime[μs, UTC]]
    [
        2017-02-03 04:05:06 UTC
        2017-02-04 04:05:06 UTC
        2017-02-05 04:05:06 UTC
        2017-02-06 04:05:06 UTC
        2017-02-07 04:05:06 UTC
    ]

    ```
    """
    return pl.datetime_range(
        start=start,
        end=find_end_datetime(
            start=start,
            periods=periods - 1,
            interval=interval,
        ),
        interval=interval,
        **kwargs,
    )

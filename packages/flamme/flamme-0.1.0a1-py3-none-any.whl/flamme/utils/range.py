r"""Contain utility functions to manage ranges of values."""

from __future__ import annotations

__all__ = ["find_range"]

import numpy as np


def find_range(
    values: np.ndarray,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
) -> tuple[float, float]:
    r"""Find a valid range of value.

    Args:
        values: The values used to find the quantiles.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.

    Returns:
        The range of values in the format ``(min, max)``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.utils.range import find_range
    >>> data = np.arange(101)
    >>> find_range(data)
    (0, 100)
    >>> find_range(data, xmin=5, xmax=50)
    (5, 50)
    >>> find_range(data, xmin="q0.1", xmax="q0.9")
    (10.0, 90.0)

    ```
    """
    if xmin is None:
        xmin = np.nanmin(values).item()
    if xmax is None:
        xmax = np.nanmax(values).item()
    q = [float(x[1:]) for x in [xmin, xmax] if isinstance(x, str)]
    quantiles = np.nanquantile(values, q)
    if isinstance(xmin, str):
        xmin = quantiles[0]
    if isinstance(xmax, str):
        xmax = quantiles[-1]
    if isinstance(xmin, np.number):
        xmin = xmin.item()
    if isinstance(xmax, np.number):
        xmax = xmax.item()
    return (xmin, xmax)

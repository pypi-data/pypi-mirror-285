r"""Contain utility functions to generate histograms."""

from __future__ import annotations

__all__ = ["adjust_nbins", "find_nbins"]

import math

import numpy as np


def adjust_nbins(nbins: int | None, array: np.ndarray) -> int | None:
    r"""Return the adjusted number of bins.

    Args:
        nbins: The initial number of bins.
        array: The array with the value to plot in the histogram.

    Returns:
        The adjusted number of bins.

    Example usage:

    ```pycon

    >>> from flamme.plot.utils.hist import adjust_nbins
    >>> nbins = adjust_nbins(nbins=100, array=np.array([1, 4, 5, 6]))
    >>> nbins
    6

    ```
    """
    if array.size == 0 or nbins is None:
        return nbins
    if np.issubdtype(array.dtype, np.integer):
        return min(nbins, (np.max(array) - np.min(array) + 1).item())
    return nbins


def find_nbins(bin_size: float, min: float, max: float) -> int:  # noqa: A002
    r"""Find the number of bins from the bin size and the range of
    values.

    Args:
        bin_size: The target bin size.
        min: The minimum value.
        max: The maximum value.

    Returns:
        The number of bins.

    Raises:
        RuntimeError: if the bin size is invalid.
        RuntimeError: if the max value is invalid.

    Example usage:

    ```pycon

    >>> from flamme.plot.utils.hist import find_nbins
    >>> nbins = find_nbins(bin_size=1, min=0, max=10)
    >>> nbins
    11

    ```
    """
    if bin_size <= 0:
        msg = f"Incorrect bin_size {bin_size}. bin_size must be greater than 0"
        raise RuntimeError(msg)
    if max < min:
        msg = f"Incorrect max {max}. max must be greater or equal to min: {min}"
        raise RuntimeError(msg)
    if min == max:
        return 1
    return math.ceil((max - min + 1) / bin_size)

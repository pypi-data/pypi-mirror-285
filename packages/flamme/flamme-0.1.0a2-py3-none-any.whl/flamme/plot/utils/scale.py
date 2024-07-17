r"""Contain scale utility functions."""

from __future__ import annotations

__all__ = ["auto_yscale_continuous", "auto_yscale_discrete"]


import numpy as np

from flamme.utils.array import nonnan


def auto_yscale_continuous(array: np.ndarray, nbins: int | None = None) -> str:
    r"""Find a good scale for y-axis based on the data distribution.

    Args:
        array: The data to use to find the scale.
        nbins: The number of bins in the histogram.

    Returns:
        The scale for y-axis.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.plot.utils import auto_yscale_continuous
    >>> auto_yscale_continuous(np.arange(100))
    linear

    ```
    """
    if nbins is None:
        nbins = 100
    array = nonnan(array)
    counts = np.histogram(array, bins=nbins)[0]
    nonzero_count = [c for c in counts if c > 0]
    if len(nonzero_count) <= 2 or (max(nonzero_count) / max(min(nonzero_count), 1)) < 50:
        return "linear"
    if np.nanmin(array) <= 0.0:
        return "symlog"
    return "log"


def auto_yscale_discrete(min_count: int, max_count: int, threshold: int = 50) -> str:
    r"""Find a good scale for y-axis based on the data distribution.

    Args:
        min_count: The minimal count value.
        max_count: The maximal count value.
        threshold: The threshold used to control the transition from
            linear to log scale. ``50`` means the ratio
            ``max_count/min_count`` must be greater than 50 to use the
            log scale. If it is lower than 50, the linear scale is
            used.

    Returns:
        The scale for y-axis.

    Example usage:

    ```pycon

    >>> from flamme.plot.utils import auto_yscale_discrete
    >>> auto_yscale_discrete(min_count=5, max_count=10)
    linear
    >>> auto_yscale_discrete(min_count=5, max_count=1000)
    log

    ```
    """
    return "log" if (max_count / max(min_count, 1)) >= threshold else "linear"

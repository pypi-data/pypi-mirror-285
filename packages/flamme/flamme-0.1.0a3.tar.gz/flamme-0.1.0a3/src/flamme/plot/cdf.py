r"""Contain CDF plotting functions."""

from __future__ import annotations

__all__ = ["plot_cdf"]

from typing import TYPE_CHECKING

import numpy as np

from flamme.utils.array import nonnan

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def plot_cdf(
    ax: Axes,
    array: np.ndarray,
    nbins: int | None = None,
    xmin: float = float("-inf"),
    xmax: float = float("inf"),
    color: str = "tab:blue",
    labelcolor: str = "black",
) -> None:
    r"""Plot the cumulative distribution function (CDF).

    Args:
        ax: The axes of the matplotlib figure to update.
        array: The array with the data.
        nbins: The number of bins to use to plot the CDF.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        color: The plot color.
        labelcolor: The label color.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import plot_cdf
    >>> fig, ax = plt.subplots()
    >>> plot_cdf(ax, array=np.arange(101))

    ```
    """
    array = nonnan(array.ravel())
    if array.size == 0:
        return
    nbins = nbins or min(1000, array.size)
    nleft = array[array < xmin].size
    nright = array[array > xmax].size
    counts, edges = np.histogram(array[np.logical_and(array >= xmin, array <= xmax)], bins=nbins)
    cdf = (np.cumsum(counts) + nleft) / (np.sum(counts) + nleft + nright)
    x = [(left + right) * 0.5 for left, right in zip(edges[:-1], edges[1:])]
    ax.tick_params(axis="y", labelcolor=labelcolor)
    ax.plot(x, cdf, color=color, label="CDF")
    ymin, ymax = max(0.0, cdf[0]), min(1.0, cdf[-1])
    if ymin < ymax:
        ax.set_ylim(ymin, ymax)
    ax.set_ylabel("cumulative distribution function (CDF)", color=labelcolor)

r"""Contain plotting functions to analyze continuous values."""

from __future__ import annotations

__all__ = [
    "boxplot_continuous",
    "boxplot_continuous_temporal",
    "hist_continuous",
    "hist_continuous2",
]

from typing import TYPE_CHECKING

import numpy as np

from flamme.plot.cdf import plot_cdf
from flamme.plot.utils import (
    auto_yscale_continuous,
    axvline_quantile,
    readable_xticklabels,
)
from flamme.utils.array import nonnan
from flamme.utils.range import find_range

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes


def boxplot_continuous(
    ax: Axes,
    array: np.ndarray,
    xmin: float | str | None = None,
    xmax: float | str | None = None,
) -> None:
    r"""Plot the histogram of an array containing continuous values.

    Args:
        ax: The axes of the matplotlib figure to update.
        array: The array with the data.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import boxplot_continuous
    >>> fig, ax = plt.subplots()
    >>> boxplot_continuous(ax, array=np.arange(101))

    ```
    """
    array = array.ravel()
    if array.size == 0:
        return
    xmin, xmax = find_range(array, xmin=xmin, xmax=xmax)
    ax.boxplot(
        array,
        notch=True,
        vert=False,
        widths=0.7,
        patch_artist=True,
        boxprops={"facecolor": "lightblue"},
    )
    readable_xticklabels(ax, max_num_xticks=100)
    if xmin < xmax:
        ax.set_xlim(xmin, xmax)
    ax.set_ylabel(" ")


def boxplot_continuous_temporal(
    ax: Axes,
    data: Sequence[np.ndarray],
    steps: Sequence,
    ymin: float | str | None = None,
    ymax: float | str | None = None,
    yscale: str = "linear",
) -> None:
    r"""Plot the histogram of an array containing continuous values.

    Args:
        ax: The axes of the matplotlib figure to update.
        data: The sequence of data where each item is a 1-d array with
            the values of the time step.
        steps: The sequence time step names.
        ymin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        ymax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.

    Raises:
        RuntimeError: if ``data`` and ``steps`` have different lengths

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import boxplot_continuous_temporal
    >>> fig, ax = plt.subplots()
    >>> rng = np.random.default_rng()
    >>> data = [rng.standard_normal(1000) for _ in range(10)]
    >>> boxplot_continuous_temporal(ax, data=data, steps=list(range(len(data))))

    ```
    """
    if len(data) == 0:
        return
    if len(data) != len(steps):
        msg = f"data and steps have different lengths: {len(data):,} vs {len(steps):,}"
        raise RuntimeError(msg)
    data = [nonnan(x) for x in data]
    ax.boxplot(
        data,
        notch=True,
        vert=True,
        widths=0.7,
        patch_artist=True,
        boxprops={"facecolor": "lightblue"},
    )
    array = np.concatenate(data)
    ymin, ymax = find_range(array, xmin=ymin, xmax=ymax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(np.arange(len(steps)), labels=steps)
    if yscale == "auto":
        yscale = auto_yscale_continuous(array=array, nbins=100)
    ax.set_yscale(yscale)
    readable_xticklabels(ax)


def hist_continuous(
    ax: Axes,
    array: np.ndarray,
    nbins: int | None = None,
    density: bool = False,
    yscale: str = "linear",
    xmin: float | str | None = None,
    xmax: float | str | None = None,
    cdf: bool = True,
    quantile: bool = True,
) -> None:
    r"""Plot the histogram of an array containing continuous values.

    Args:
        ax: The axes of the matplotlib figure to update.
        array: The array with the data.
        nbins: The number of bins to use to plot.
        density: If True, draw and return a probability density:
            each bin will display the bin's raw count divided by the
            total number of counts and the bin width, so that the area
            under the histogram integrates to 1.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        cdf: If ``True``, the CDF is added to the plot.
        quantile: If ``True``, the 5% and 95% quantiles are added to
            the plot.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import hist_continuous
    >>> fig, ax = plt.subplots()
    >>> hist_continuous(ax, array=np.arange(101))

    ```
    """
    array = array.ravel()
    if array.size == 0:
        return
    xmin, xmax = find_range(array, xmin=xmin, xmax=xmax)
    ax.hist(array, bins=nbins, range=(xmin, xmax), color="tab:blue", alpha=0.9, density=density)
    readable_xticklabels(ax, max_num_xticks=100)
    if xmin < xmax:
        ax.set_xlim(xmin, xmax)
    ax.set_ylabel("density (number of occurrences/total)" if density else "number of occurrences")
    if yscale == "auto":
        yscale = auto_yscale_continuous(array=array, nbins=nbins)
    ax.set_yscale(yscale)
    if cdf:
        plot_cdf(
            ax=ax.twinx(),
            array=array,
            nbins=nbins,
            xmin=xmin,
            xmax=xmax,
            color="tab:red",
            labelcolor="tab:red",
        )

    if not quantile:
        return
    q05, q95 = np.quantile(array, q=[0.05, 0.95])
    if xmin < q05 < xmax:
        axvline_quantile(ax, quantile=q05, label="q0.05 ", horizontalalignment="right")
    if xmin < q95 < xmax:
        axvline_quantile(ax, quantile=q95, label=" q0.95", horizontalalignment="left")


def hist_continuous2(
    ax: Axes,
    array1: np.ndarray,
    array2: np.ndarray,
    label1: str = "first",
    label2: str = "second",
    nbins: int | None = None,
    density: bool = False,
    yscale: str = "linear",
    xmin: float | str | None = None,
    xmax: float | str | None = None,
) -> None:
    r"""Plot the histogram of two arrays to compare the distributions.

    Args:
        ax: The axes of the matplotlib figure to update.
        array1: The first array with the data.
        array2: The second array with the data.
        label1: The label associated to the first array.
        label2: The label associated to the second array.
        nbins: The number of bins to use to plot.
        density: If True, draw and return a probability density:
            each bin will display the bin's raw count divided by the
            total number of counts and the bin width, so that the area
            under the histogram integrates to 1.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        xmin: The minimum value of the range or its
            associated quantile. ``q0.1`` means the 10% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.
        xmax: The maximum value of the range or its
            associated quantile. ``q0.9`` means the 90% quantile.
            ``0`` is the minimum value and ``1`` is the maximum value.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import hist_continuous2
    >>> fig, ax = plt.subplots()
    >>> hist_continuous2(ax, array1=np.arange(101), array2=np.arange(51))

    ```
    """
    array1, array2 = array1.ravel(), array2.ravel()
    array = np.concatenate([array1, array2])
    if array.size == 0:
        return
    xmin, xmax = find_range(array, xmin=xmin, xmax=xmax)
    ax.hist(
        array1,
        bins=nbins,
        range=(xmin, xmax),
        color="tab:blue",
        alpha=0.5,
        label=label1,
        density=density,
    )
    ax.hist(
        array2,
        bins=nbins,
        range=(xmin, xmax),
        color="tab:orange",
        alpha=0.5,
        label=label2,
        density=density,
    )
    readable_xticklabels(ax, max_num_xticks=100)
    if xmin < xmax:
        ax.set_xlim(xmin, xmax)
    ax.set_ylabel("density (number of occurrences/total)" if density else "number of occurrences")
    if yscale == "auto":
        yscale = auto_yscale_continuous(array=array, nbins=nbins)
    ax.set_yscale(yscale)
    ax.legend()

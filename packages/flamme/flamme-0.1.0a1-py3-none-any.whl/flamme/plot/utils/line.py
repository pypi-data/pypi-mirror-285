r"""Contain utility functions to draw lines."""

from __future__ import annotations

__all__ = ["axvline_quantile", "axvline_median"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def axvline_quantile(
    ax: Axes,
    quantile: float,
    label: str,
    color: str = "black",
    linestyle: str = "dashed",
    horizontalalignment: str = "center",
) -> None:
    r"""Add a vertical line to represent a quantile value.

    Args:
        ax: The Axes object that encapsulates all the elements of an
            individual (sub-)plot in a figure.
        quantile: The quantile value.
        label: The associated label to show on the plot.
        color: The line color.
        linestyle: The line style.
        horizontalalignment: The horizontal alignment relative to
            the anchor point.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot.utils import axvline_quantile
    >>> fig, ax = plt.subplots()
    >>> axvline_quantile(ax, quantile=42.0, label=" q0.9")

    ```
    """
    ax.axvline(quantile, color=color, linestyle=linestyle)
    ax.text(
        quantile,
        0.99,
        label,
        transform=ax.get_xaxis_transform(),
        color=color,
        horizontalalignment=horizontalalignment,
        verticalalignment="top",
    )


def axvline_median(
    ax: Axes,
    median: float,
    label: str = "median",
    color: str = "black",
    linestyle: str = "dashed",
    horizontalalignment: str = "center",
) -> None:
    r"""Add a vertical line to represent the median value.

    Args:
        ax: The Axes object that encapsulates all the elements of an
            individual (sub-)plot in a figure.
        median: The median value.
        label: The associated label to show on the plot.
        color: The line color.
        linestyle: The line style.
        horizontalalignment: The horizontal alignment relative to
            the anchor point.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot.utils import axvline_median
    >>> fig, ax = plt.subplots()
    >>> axvline_median(ax, median=42.0)

    ```
    """
    ax.axvline(median, color=color, linestyle=linestyle)
    ax.text(
        median,
        0.99,
        label,
        transform=ax.get_xaxis_transform(),
        color=color,
        horizontalalignment=horizontalalignment,
        verticalalignment="top",
    )

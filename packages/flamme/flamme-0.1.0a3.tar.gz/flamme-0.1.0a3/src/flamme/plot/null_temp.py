r"""Contain functionalities to plot the temporal distribution of the
number of missing values."""

from __future__ import annotations

__all__ = ["plot_null_temporal"]

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes


def plot_null_temporal(ax: Axes, nulls: Sequence, totals: Sequence, labels: Sequence) -> None:
    r"""Plot the temporal distribution of the number of missing values.

    ``nulls``, ``totals``, and ``labels`` must have the same length
    and have the same order.

    Args:
        ax: The Axes object that encapsulates all the elements of an
            individual (sub-)plot in a figure.
        nulls: The number of null values for each temporal period.
        totals: The number of total values for each temporal period.
        labels: The labels for each temporal period.

    Raises:
        RuntimeError: if ``nulls``, ``totals``, and ``labels`` have
            different lengths.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import plot_null_temporal
    >>> fig, ax = plt.subplots()
    >>> plot_null_temporal(
    ...     ax, nulls=[1, 2, 3, 4], totals=[10, 12, 14, 16], labels=["jan", "feb", "mar", "apr"]
    ... )

    ```
    """
    if len(nulls) != len(totals):
        msg = f"nulls ({len(nulls):,}) and totals ({len(totals):,}) have different lengths"
        raise RuntimeError(msg)
    if len(labels) != len(totals):
        msg = f"nulls ({len(nulls):,}) and labels ({len(labels):,}) have different lengths"
        raise RuntimeError(msg)
    if len(nulls) == 0:
        return

    labels = list(map(str, labels))
    nulls = np.asarray(nulls)
    totals = np.asarray(totals)

    color = "tab:blue"
    x = np.arange(len(labels))
    ax.set_ylabel("number of null/total values", color=color)
    ax.tick_params(axis="y", labelcolor=color)
    ax.bar(x=x, height=totals, color="tab:cyan", alpha=0.5, label="total")
    ax.bar(x=x, height=nulls, color=color, alpha=0.8, label="null")
    ax.legend()

    ax2 = ax.twinx()
    color = "black"
    ax2.set_ylabel("percentage", color=color)
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.plot(x, nulls / totals, "o-", color=color)

    ax.set_xticks(x, labels=labels)
    ax.set_xlim(-0.5, len(labels) - 0.5)

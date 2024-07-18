r"""Contain plotting functions to analyze discrete values."""

from __future__ import annotations

__all__ = ["bar_discrete", "bar_discrete_temporal"]

from typing import TYPE_CHECKING

import numpy as np
from matplotlib import pyplot as plt

from flamme.plot.utils import auto_yscale_discrete, readable_xticklabels

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes


def bar_discrete(
    ax: Axes,
    names: Sequence,
    counts: Sequence[int],
    yscale: str = "auto",
) -> None:
    r"""Plot the histogram of an array containing discrete values.

    Args:
        ax: The axes of the matplotlib figure to update.
        names: The name of the values to plot.
        counts: The number of value occurrences.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import bar_discrete
    >>> fig, ax = plt.subplots()
    >>> bar_discrete(ax, names=["a", "b", "c", "d"], counts=[5, 100, 42, 27])

    ```
    """
    n = len(names)
    if n == 0:
        return
    x = np.arange(n)
    ax.bar(x, counts, width=0.9 if n < 50 else 1, color="tab:blue")
    if yscale == "auto":
        yscale = auto_yscale_discrete(min_count=min(counts), max_count=max(counts))
    ax.set_yscale(yscale)
    ax.set_xticks(x, labels=map(str, names))
    readable_xticklabels(ax, max_num_xticks=100)
    ax.set_xlim(-0.5, len(names) - 0.5)
    ax.set_xlabel("values")
    ax.set_ylabel("number of occurrences")


def bar_discrete_temporal(
    ax: Axes,
    counts: np.ndarray,
    steps: Sequence | None = None,
    values: Sequence | None = None,
    proportion: bool = False,
) -> None:
    r"""Plot the temporal distribution of discrete values.

    Args:
        ax: The axes of the matplotlib figure to update.
        counts: A 2-d array that indicates the number of occurrences
            for each value and time step. The first dimension
            represents the value and the second dimension
            represents the steps.
        steps: The name associated to each step.
        values: The name associated to each value.
        proportion: If ``True``, it plots the normalized number of
            occurrences for each step.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from flamme.plot import bar_discrete_temporal
    >>> fig, ax = plt.subplots()
    >>> bar_discrete_temporal(
    ...     ax, counts=np.ones((5, 20)), values=list(range(5)), steps=list(range(20))
    ... )

    ```
    """
    if counts.size == 0:
        return
    num_values, num_steps = counts.shape
    values = _prepare_values_bar_discrete_temporal(values=values, num_values=num_values)
    steps = _prepare_steps_bar_discrete_temporal(steps=steps, num_steps=num_steps)
    counts = _prepare_counts_bar_discrete_temporal(counts=counts, proportion=proportion)

    x = np.arange(num_steps, dtype=np.int64)
    bottom = np.zeros(num_steps, dtype=counts.dtype)
    width = 0.9 if num_steps < 50 else 1
    my_cmap = plt.get_cmap("viridis")
    for i in range(num_values):
        count = counts[i]
        ax.bar(x, count, label=values[i], bottom=bottom, width=width, color=my_cmap(i / num_values))
        bottom += count

    num_valid_values = len(list(filter(lambda x: x is not None, values)))
    if num_valid_values <= 10 and num_valid_values > 0:
        ax.legend()
    ax.set_xticks(x, labels=steps)
    readable_xticklabels(ax, max_num_xticks=100)
    ax.set_xlim(-0.5, num_steps - 0.5)
    ax.set_ylabel("steps")
    ax.set_ylabel("proportion" if proportion else "number of occurrences")


def _prepare_values_bar_discrete_temporal(values: Sequence | None, num_values: int) -> list:
    r"""Return the list of values.

    This function was designed to be used in ``bar_discrete_temporal``.

    Args:
        values: The sequence of values.
        num_values: The expected number of values.

    Returns:
        The values. If ``values`` is ``None``, a list filled with
            ``None`` is returned.

    Raises:
        RuntimeError: if the length of ``values`` does not match with
            ``num_values``.
    """
    if values is None:
        return [None] * num_values
    if len(values) != num_values:
        msg = (
            f"values length ({len(values):,}) do not match with the count matrix "
            f"first dimension ({num_values:,})"
        )
        raise RuntimeError(msg)
    return list(values)


def _prepare_steps_bar_discrete_temporal(steps: Sequence | None, num_steps: int) -> list:
    r"""Return the list of steps.

    This function was designed to be used in ``bar_discrete_temporal``.

    Args:
        steps: The sequence of steps.
        num_steps: The expected number of steps.

    Returns:
        The steps. If ``steps`` is ``None``, a list filled with
            ``None`` is returned.

    Raises:
        RuntimeError: if the length of ``steps`` does not match with
            ``num_steps``.
    """
    if steps is None:
        return list(range(num_steps))
    if len(steps) != num_steps:
        msg = (
            f"steps length ({len(steps):,}) do not match with the count matrix "
            f"second dimension ({num_steps:,})"
        )
        raise RuntimeError(msg)
    return list(steps)


def _prepare_counts_bar_discrete_temporal(counts: np.ndarray, proportion: bool) -> np.ndarray:
    r"""Prepare the count matrix.

    This function was designed to be used in ``bar_discrete_temporal``.

    Args:
        counts: A 2-d array that indicates the number of occurrences
            for each value and time step. The first dimension
            represents the value and the second dimension
            represents the steps.
        proportion: If ``True``, the count matrix is normalized number
            of occurrences for each step.

    Returns:
        The count matrix.
    """
    if not proportion:
        return counts
    return counts / np.clip(counts.sum(axis=0), a_min=1, a_max=None)

r"""Contain plotting functionalities."""

from __future__ import annotations

__all__ = [
    "bar_discrete",
    "bar_discrete_temporal",
    "boxplot_continuous",
    "boxplot_continuous_temporal",
    "hist_continuous",
    "hist_continuous2",
    "plot_cdf",
    "plot_null_temporal",
]

from flamme.plot.cdf import plot_cdf
from flamme.plot.continuous import (
    boxplot_continuous,
    boxplot_continuous_temporal,
    hist_continuous,
    hist_continuous2,
)
from flamme.plot.discrete import bar_discrete, bar_discrete_temporal
from flamme.plot.null_temp import plot_null_temporal

r"""Contain statistics utility functions."""

from __future__ import annotations

__all__ = [
    "compute_statistics_continuous",
    "compute_statistics_continuous_array",
    "compute_statistics_continuous_series",
    "quantile",
]

from typing import TYPE_CHECKING

import numpy as np
import polars as pl
from scipy.stats import kurtosis, skew

from flamme.utils.array import nonnan

if TYPE_CHECKING:
    from collections.abc import Sequence


def compute_statistics_continuous(data: np.ndarray | pl.Series) -> dict[str, float]:
    r"""Return several descriptive statistics for the data with
    continuous values.

    Args:
        data: The data to analyze.

    Returns:
        The descriptive statistics for the input data.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.utils.stats import compute_statistics_continuous
    >>> compute_statistics_continuous(np.arange(101))
    {'count': 101, 'nunique': 101, 'num_non_nulls': 101, 'num_nulls': 0,
     'mean': 50.0, 'std': 29.15...,
     'skewness': 0.0, 'kurtosis': -1.20..., 'min': 0.0, 'q001': 0.1, 'q01': 1.0,
     'q05': 5.0, 'q10': 10.0, 'q25': 25.0, 'median': 50.0, 'q75': 75.0, 'q90': 90.0,
     'q95': 95.0, 'q99': 99.0, 'q999': 99.9, 'max': 100.0, '>0': 100, '<0': 0, '=0': 1}

    ```
    """
    if isinstance(data, pl.Series):
        return compute_statistics_continuous_series(data)
    return compute_statistics_continuous_array(data)


def compute_statistics_continuous_array(array: np.ndarray) -> dict[str, float]:
    r"""Return several descriptive statistics for the data with
    continuous values.

    Args:
        array: The data to analyze.

    Returns:
        The descriptive statistics for the input data.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.utils.stats import compute_statistics_continuous_array
    >>> compute_statistics_continuous_array(np.arange(101))
    {'count': 101, 'nunique': 101, 'num_non_nulls': 101, 'num_nulls': 0,
     'mean': 50.0, 'std': 29.15...,
     'skewness': 0.0, 'kurtosis': -1.20..., 'min': 0.0, 'q001': 0.1, 'q01': 1.0,
     'q05': 5.0, 'q10': 10.0, 'q25': 25.0, 'median': 50.0, 'q75': 75.0, 'q90': 90.0,
     'q95': 95.0, 'q99': 99.0, 'q999': 99.9, 'max': 100.0, '>0': 100, '<0': 0, '=0': 1}

    ```
    """
    array = array.ravel().astype(np.float64)
    array_nonnan = nonnan(array)
    stats = {
        "count": int(array.size),
        "nunique": int(np.unique(array).size),
        "num_non_nulls": int(array_nonnan.size),
    }
    stats["num_nulls"] = stats["count"] - stats["num_non_nulls"]
    if array_nonnan.size == 0:
        return stats | {
            "mean": float("nan"),
            "std": float("nan"),
            "skewness": float("nan"),
            "kurtosis": float("nan"),
            "min": float("nan"),
            "q001": float("nan"),
            "q01": float("nan"),
            "q05": float("nan"),
            "q10": float("nan"),
            "q25": float("nan"),
            "median": float("nan"),
            "q75": float("nan"),
            "q90": float("nan"),
            "q95": float("nan"),
            "q99": float("nan"),
            "q999": float("nan"),
            "max": float("nan"),
            ">0": 0,
            "<0": 0,
            "=0": 0,
        }
    quantiles = quantile(
        array_nonnan, q=[0.001, 0.01, 0.05, 0.1, 0.25, 0.75, 0.9, 0.95, 0.99, 0.999]
    )
    return stats | {
        "mean": np.mean(array_nonnan).item(),
        "std": np.std(array_nonnan).item(),
        "skewness": skew(array_nonnan).item(),
        "kurtosis": kurtosis(array_nonnan).item(),
        "min": np.min(array_nonnan).item(),
        "q001": quantiles[0.001],
        "q01": quantiles[0.01],
        "q05": quantiles[0.05],
        "q10": quantiles[0.1],
        "q25": quantiles[0.25],
        "median": np.median(array_nonnan).item(),
        "q75": quantiles[0.75],
        "q90": quantiles[0.9],
        "q95": quantiles[0.95],
        "q99": quantiles[0.99],
        "q999": quantiles[0.999],
        "max": np.max(array_nonnan).item(),
        ">0": (array > 0).sum().item(),
        "<0": (array < 0).sum().item(),
        "=0": (array == 0).sum().item(),
    }


def compute_statistics_continuous_series(series: pl.Series) -> dict[str, float]:
    r"""Return several descriptive statistics for the data with
    continuous values.

    Args:
        series: The series to analyze.

    Returns:
        The descriptive statistics for the input data.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.utils.stats import compute_statistics_continuous_series
    >>> compute_statistics_continuous_series(pl.Series(list(range(101))))
    {'count': 101, 'nunique': 101, 'num_non_nulls': 101, 'num_nulls': 0,
     'mean': 50.0, 'std': 29.15...,
     'skewness': 0.0, 'kurtosis': -1.20..., 'min': 0.0, 'q001': 0.1, 'q01': 1.0,
     'q05': 5.0, 'q10': 10.0, 'q25': 25.0, 'median': 50.0, 'q75': 75.0, 'q90': 90.0,
     'q95': 95.0, 'q99': 99.0, 'q999': 99.9, 'max': 100.0, '>0': 100, '<0': 0, '=0': 1}

    ```
    """
    stats = {
        "count": int(series.shape[0]),
        "nunique": series.n_unique(),
        "num_nulls": int(series.null_count()),
    }
    stats["num_non_nulls"] = stats["count"] - stats["num_nulls"]
    return compute_statistics_continuous_array(series.drop_nulls().to_numpy()) | stats


def quantile(array: np.ndarray, q: Sequence[float]) -> dict[float, float]:
    r"""Compute the q-th quantile of the data.

    Args:
        array: The input data.
        q: The quantiles to compute. Values must be between 0 and 1
            inclusive.

    Returns:
        A dictionary with the quantiles values.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from flamme.utils.stats import quantile
    >>> quantile(np.arange(101), q=[0.001, 0.01, 0.05, 0.1, 0.25, 0.75, 0.9, 0.95, 0.99, 0.999])
    {0.001: 0.1, 0.01: 1.0, 0.05: 5.0, 0.1: 10.0, 0.25: 25.0, 0.75: 75.0,
     0.9: 90.0, 0.95: 95.0, 0.99: 99.0, 0.999: 99.9}

    ```
    """
    array = array.ravel()
    if array.size == 0:
        return {v: float("nan") for v in q}
    return dict(zip(q, np.quantile(array.astype(np.float64), q).tolist()))

r"""Contain the implementation of a section to analyze a column with
discrete values."""

from __future__ import annotations

__all__ = [
    "ColumnDiscreteSection",
    "create_histogram",
    "create_histogram_section",
    "create_section_template",
    "create_table",
    "create_table_row",
]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping
from jinja2 import Template
from matplotlib import pyplot as plt

from flamme.plot import bar_discrete
from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.figure import MISSING_FIGURE_MESSAGE, figure2html

if TYPE_CHECKING:
    from collections import Counter
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class ColumnDiscreteSection(BaseSection):
    r"""Implement a section that analyzes a discrete distribution of
    values.

    Args:
        counter: The counter that represents the discrete
            distribution.
        null_values: The number of null values.
        column: The column name.
        max_rows: The maximum number of rows to show in the
            table.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from flamme.section import ColumnDiscreteSection
    >>> section = ColumnDiscreteSection(counter=Counter({"a": 4, "b": 2, "c": 6}), column="col")
    >>> section
    ColumnDiscreteSection(
      (null_values): 0
      (column): col
      (yscale): auto
      (max_rows): 20
      (figsize): None
    )
    >>> section.get_statistics()
    {'most_common': [('c', 6), ('a', 4), ('b', 2)], 'null_values': 0, 'nunique': 3, 'total': 12}

    ```
    """

    def __init__(
        self,
        counter: Counter,
        null_values: int = 0,
        column: str = "N/A",
        max_rows: int = 20,
        yscale: str = "auto",
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._counter = counter
        self._null_values = null_values
        self._column = column
        self._max_rows = int(max_rows)
        self._yscale = yscale
        self._figsize = figsize

        self._total = sum(self._counter.values())

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "null_values": self._null_values,
                    "column": self._column,
                    "yscale": self._yscale,
                    "max_rows": self._max_rows,
                    "figsize": self._figsize,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    @property
    def yscale(self) -> str:
        return self._yscale

    def get_statistics(self) -> dict:
        most_common = [(value, count) for value, count in self._counter.most_common() if count > 0]
        return {
            "most_common": most_common,
            "null_values": self._null_values,
            "nunique": len(most_common),
            "total": self._total,
        }

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the discrete distribution of {self._column}")
        stats = self.get_statistics()
        null_values_pct = (
            f"{100 * self._null_values / stats['total']:.2f}" if stats["total"] > 0 else "N/A"
        )
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "column": self._column,
                "total_values": f"{stats['total']:,}",
                "unique_values": f"{stats['nunique']:,}",
                "null_values": f"{self._null_values:,}",
                "null_values_pct": null_values_pct,
                "figure": create_histogram_section(
                    counter=self._counter,
                    column=self._column,
                    yscale=self._yscale,
                    figsize=self._figsize,
                ),
                "table": create_table(
                    column=self._column,
                    counter=self._counter,
                    max_rows=self._max_rows,
                ),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.discrete import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the discrete distribution of values for column <em>{{column}}</em>.

<ul>
<li> total values: {{total_values}} </li>
<li> number of unique values: {{unique_values}} </li>
<li> number of null values: {{null_values}} / {{total_values}} ({{null_values_pct}}%) </li>
</ul>

{{figure}}
{{table}}

<p style="margin-top: 1rem;">
"""


def create_histogram_section(
    counter: Counter,
    column: str = "N/A",
    yscale: str = "auto",
    figsize: tuple[float, float] | None = None,
) -> str:
    r"""Return the histogram section.

    Args:
        counter: The counter that represents the discrete
            distribution.
        column: The column name.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'`` scale is chosen based on the
            distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The histogram section.

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from flamme.section.discrete import create_histogram_section
    >>> section = create_histogram_section(
    ...     counter=Counter({"a": 4, "b": 2, "c": 6}), column="col"
    ... )

    ```
    """
    if sum(counter.values()) == 0:
        return MISSING_FIGURE_MESSAGE
    most_common = [(value, count) for value, count in counter.most_common() if count > 0]
    fig = create_histogram(
        column=column,
        names=[str(value) for value, _ in most_common],
        counts=[count for _, count in most_common],
        yscale=yscale,
        figsize=figsize,
    )
    return Template(
        r"""<p style="margin-top: 1rem;">
<b>Distribution of values in column {{column}}</b>

<p>The values in the figure below are sorted by decreasing order of number of occurrences.

{{figure}}
"""
    ).render({"figure": figure2html(fig, close_fig=True), "column": column})


def create_histogram(
    column: str,
    names: Sequence,
    counts: Sequence[int],
    yscale: str = "auto",
    figsize: tuple[float, float] | None = None,
) -> plt.Figure | None:
    r"""Return a figure with the histogram of discrete values.

    Args:
        column: The column name.
        names: The name of the values to plot.
        counts: The number of value occurrences.
        yscale: The y-axis scale. If ``'auto'``, the
            ``'linear'`` or ``'log'/'symlog'`` scale is chosen based
            on the distribution.
        figsize: The figure size in inches. The first
            dimension is the width and the second is the height.

    Returns:
        The generated figure.

    Example usage:

    ```pycon

    >>> from flamme.section.discrete import create_histogram
    >>> fig = create_histogram(
    ...     column="col", names=["a", "b", "c", "d"], counts=[5, 100, 42, 27]
    ... )

    ```
    """
    if sum(counts) == 0:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    bar_discrete(ax=ax, names=names, counts=counts, yscale=yscale)
    ax.set_title(f"number of occurrences for each value of {column}")
    return fig


def create_table(
    counter: Counter,
    column: str = "N/A",
    max_rows: int = 20,
) -> str:
    r"""Return a HTML table with the discrete distribution.

    Args:
        counter: The counter that represents the discrete
            distribution.
        column: The column name.
        max_rows: The maximum number of rows to show in the
            table.

    Returns:
        The generated table.

    Example usage:

    ```pycon

    >>> from collections import Counter
    >>> from flamme.section.discrete import create_table_row
    >>> table = create_table(counter=Counter({"a": 4, "b": 2, "c": 6}), column="col")

    ```
    """
    if sum(counter.values()) == 0:
        return "<span>&#9888;</span> No table is generated because the column is empty"

    most_common = counter.most_common(max_rows)
    rows_head = "\n".join([create_table_row(column=col, count=count) for col, count in most_common])
    lest_common = counter.most_common()[-max_rows:][::-1]
    rows_tail = "\n".join([create_table_row(column=col, count=count) for col, count in lest_common])
    return Template(
        """<details>
    <summary>[show head and tail values]</summary>

    <div class="row">
      <div class="col">
        <p style="margin-top: 1rem;">
        <b>Head: {{max_values}} most common values in column <em>{{column}}</em></b>
        <table class="table table-hover table-responsive w-auto" >
            <thead class="thead table-group-divider">
                <tr>
                    <th>column</th>
                    <th>count</th>
                </tr>
            </thead>
            <tbody class="tbody table-group-divider">
                {{rows_head}}
                <tr class="table-group-divider"></tr>
            </tbody>
        </table>
      </div>
      <div class="col">
        <p style="margin-top: 1rem;">
        <b>Tail: {{max_values}} least common values in column <em>{{column}}</em></b>
        <table class="table table-hover table-responsive w-auto" >
            <thead class="thead table-group-divider">
                <tr>
                    <th>column</th>
                    <th>count</th>
                </tr>
            </thead>
            <tbody class="tbody table-group-divider">
                {{rows_tail}}
                <tr class="table-group-divider"></tr>
            </tbody>
        </table>
      </div>
    </div>
</details>
"""
    ).render(
        {
            "max_values": len(most_common),
            "rows_head": rows_head,
            "rows_tail": rows_tail,
            "column": column,
        }
    )


def create_table_row(column: str, count: int) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        count (int): The count for the column.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from flamme.section.discrete import create_table_row
    >>> row = create_table_row(column="col", count=5)

    ```
    """
    return f'<tr><th>{column}</th><td style="text-align: right;">{count:,}</td></tr>'

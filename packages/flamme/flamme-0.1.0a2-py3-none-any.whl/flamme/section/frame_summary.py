r"""Contain the implementation of a section to generate a summary of a
DataFrame."""

from __future__ import annotations

__all__ = [
    "DataFrameSummarySection",
    "create_section_template",
    "create_table",
    "create_table_row",
]

import logging
from collections import Counter
from typing import TYPE_CHECKING, Any

from jinja2 import Template

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.count import compute_nunique
from flamme.utils.null import compute_null_count

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class DataFrameSummarySection(BaseSection):
    r"""Implement a section that returns a summary of a DataFrame.

    Args:
        frame: The DataFrame to analyze.
        top: The number of most frequent values to show.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section import DataFrameSummarySection
    >>> section = DataFrameSummarySection(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col1": [1.2, 4.2, 4.2, 2.2],
    ...             "col2": [1, 1, 1, 1],
    ...             "col3": [1, 2, 2, 2],
    ...         },
    ...         schema={"col1": pl.Float64, "col2": pl.Int64, "col3": pl.Int64},
    ...     )
    ... )
    >>> section
    DataFrameSummarySection(top=5)
    >>> section.get_statistics()
    {'columns': ('col1', 'col2', 'col3'), 'null_count': (0, 0, 0), 'nunique': (3, 1, 2),
     'dtypes': (Float64, Int64, Int64)}

    ```
    """

    def __init__(self, frame: pl.DataFrame, top: int = 5) -> None:
        self._frame = frame
        if top < 0:
            msg = f"Incorrect top value ({top}). top must be positive"
            raise ValueError(msg)
        self._top = top

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(top={self._top})"

    @property
    def frame(self) -> pl.DataFrame:
        r"""The DataFrame to analyze."""
        return self._frame

    @property
    def top(self) -> int:
        return self._top

    def get_columns(self) -> tuple[str, ...]:
        return tuple(self._frame.columns)

    def get_null_count(self) -> tuple[int, ...]:
        return tuple(compute_null_count(self._frame).tolist())

    def get_nunique(self) -> tuple[int, ...]:
        return tuple(compute_nunique(self._frame).tolist())

    def get_dtypes(self) -> tuple[pl.DataType, ...]:
        return tuple(self._frame.schema.dtypes())

    def get_most_frequent_values(self, top: int = 5) -> tuple[tuple[tuple[Any, int], ...], ...]:
        return tuple(tuple(Counter(series.to_list()).most_common(top)) for series in self.frame)

    def get_statistics(self) -> dict:
        return {
            "columns": self.get_columns(),
            "null_count": self.get_null_count(),
            "nunique": self.get_nunique(),
            "dtypes": self.get_dtypes(),
        }

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Rendering the DataFrame summary section...")
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "table": self._create_table(),
                "nrows": f"{self._frame.shape[0]:,}",
                "ncols": f"{self._frame.shape[1]:,}",
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)

    def _create_table(self) -> str:
        return create_table(
            columns=self.get_columns(),
            null_count=self.get_null_count(),
            nunique=self.get_nunique(),
            dtypes=self.get_dtypes(),
            most_frequent_values=self.get_most_frequent_values(top=self._top),
            total=self._frame.shape[0],
        )


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.frame_summary import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """
<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section shows a short summary of each column.

<ul>
  <li> <b>column</b>: are the column names</li>
  <li> <b>types</b>: are the real object types for the objects in the column </li>
  <li> <b>null</b>: are the number (and percentage) of null values in the column </li>
  <li> <b>unique</b>: are the number (and percentage) of unique values in the column </li>
</ul>

<p style="margin-top: 1rem;">
<b>General statistics about the DataFrame</b>

<ul>
  <li> number of rows: {{nrows}}</li>
  <li> number of columns: {{ncols}} </li>
</ul>

{{table}}

<p style="margin-top: 1rem;">
"""


def create_table(
    columns: Sequence[str],
    null_count: Sequence[int],
    nunique: Sequence[int],
    dtypes: Sequence[pl.DataType],
    most_frequent_values: Sequence[Sequence[tuple[Any, int]]],
    total: int,
) -> str:
    r"""Return a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        columns: The column names.
        null_count: The number of null values for each column.
        nunique: The number of unique values for each column.
        dtypes: The data type for each column.
        most_frequent_values: The most frequent values for each column.
        total: The total number of rows.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.frame_summary import create_table_row
    >>> row = create_table(
    ...     columns=["float", "int", "str"],
    ...     null_count=(1, 0, 2),
    ...     nunique=(5, 2, 4),
    ...     dtypes=(pl.Float64(), pl.Int64(), pl.String()),
    ...     most_frequent_values=(
    ...         ((2.2, 2), (1.2, 1), (4.2, 1), (None, 1), (1.0, 1)),
    ...         ((1, 5), (0, 1)),
    ...         (("B", 2), (None, 2), ("A", 1), ("C", 1)),
    ...     ),
    ...     total=42,
    ... )

    ```
    """
    rows = []
    for (
        column,
        null,
        nuniq,
        dtype,
        mf_values,
    ) in zip(columns, null_count, nunique, dtypes, most_frequent_values):
        rows.append(
            create_table_row(
                column=column,
                null=null,
                dtype=dtype,
                nunique=nuniq,
                most_frequent_values=mf_values,
                total=total,
            )
        )
    rows = "\n".join(rows)
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>types</th>
            <th>null</th>
            <th>unique</th>
            <th>most frequent values</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": rows})


def create_table_row(
    column: str,
    null: int,
    nunique: int,
    dtype: pl.DataType,
    most_frequent_values: Sequence[tuple[Any, int]],
    total: int,
) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        null: The number of null values.
        nunique: The number of unique values.
        dtype: The data type of the column.
        most_frequent_values: The most frequent values.
        total: The total number of rows.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.frame_summary import create_table_row
    >>> row = create_table_row(
    ...     column="col",
    ...     null=5,
    ...     nunique=42,
    ...     dtype=pl.Float64(),
    ...     most_frequent_values=[("C", 12), ("A", 5), ("B", 4)],
    ...     total=100,
    ... )

    ```
    """
    null = f"{null:,} ({100 * null / total if total else float('nan'):.2f}%)"
    nunique = f"{nunique:,} ({100 * nunique / total if total else float('nan'):.2f}%)"
    most_frequent_values = ", ".join(
        [f"{val} ({100 * c / total:.2f}%)" for val, c in most_frequent_values]
    )
    return Template(
        """<tr>
    <th>{{column}}</th>
    <td>{{dtype}}</td>
    <td {{num_style}}>{{null}}</td>
    <td {{num_style}}>{{nunique}}</td>
    <td>{{most_frequent_values}}</td>
</tr>"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "column": column,
            "null": null,
            "dtype": dtype,
            "nunique": nunique,
            "most_frequent_values": most_frequent_values,
        }
    )

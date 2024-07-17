r"""Contain the implementation of a section to analyze the duplicate
values."""

from __future__ import annotations

__all__ = ["DuplicatedRowSection", "create_section_template", "create_duplicate_table"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping
from jinja2 import Template

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl


logger = logging.getLogger(__name__)


class DuplicatedRowSection(BaseSection):
    r"""Implement a section to analyze the number of duplicated rows.

    Args:
        frame: The DataFrame to analyze.
        columns: The columns used to compute the duplicated rows.
            ``None`` means all the columns.
        figsize: The figure
            size in inches. The first dimension is the width and the
            second is the height.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> import numpy as np
    >>> from flamme.section import DuplicatedRowSection
    >>> section = DuplicatedRowSection(
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
    DuplicatedRowSection(
      (frame): (4, 3)
      (columns): None
      (figsize): None
    )
    >>> section.get_statistics()
    {'num_rows': 4, 'num_unique_rows': 3}

    ```
    """

    def __init__(
        self,
        frame: pl.DataFrame,
        columns: Sequence[str] | None = None,
        figsize: tuple[float, float] | None = None,
    ) -> None:
        self._frame = frame
        self._columns = columns if columns is None else tuple(columns)
        self._figsize = figsize

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {"frame": self._frame.shape, "columns": self._columns, "figsize": self._figsize}
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    @property
    def frame(self) -> pl.DataFrame:
        r"""The DataFrame to analyze."""
        return self._frame

    @property
    def columns(self) -> tuple[str, ...] | None:
        r"""Tuple or ``None``: The columns used to compute the
        duplicated rows."""
        return self._columns

    @property
    def figsize(self) -> tuple[float, float] | None:
        r"""The individual figure size in pixels.

        The first dimension is the width and the second is the height.
        """
        return self._figsize

    def get_statistics(self) -> dict:
        frame_no_duplicate = self._frame.unique(subset=self._columns)
        return {"num_rows": self._frame.shape[0], "num_unique_rows": frame_no_duplicate.shape[0]}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info(f"Rendering the duplicated rows section using the columns: {self._columns}")
        stats = self.get_statistics()
        columns = self._frame.columns if self._columns is None else self._columns
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "columns": ", ".join(columns),
                "num_columns": f"{len(columns):,}",
                "table": create_duplicate_table(
                    num_rows=stats["num_rows"], num_unique_rows=stats["num_unique_rows"]
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

    >>> from flamme.section.duplicate import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """
<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section shows the number of unique and duplicated rows when considering the following
{{num_columns}} columns: <em>{{columns}}</em>.

{{table}}

<p style="margin-top: 1rem;">
"""


def create_duplicate_table(num_rows: int, num_unique_rows: int) -> str:
    r"""Return a HTML table with information about duplicated rows.

    Args:
        num_rows: The number of rows.
        num_unique_rows: The number of unique rows.

    Returns:
        The HTML table with information about duplicated rows.

    Example usage:

    ```pycon

    >>> from flamme.section.duplicate import create_duplicate_table
    >>> table = create_duplicate_table(num_rows=10, num_unique_rows=5)

    ```
    """
    num_duplicated_rows = num_rows - num_unique_rows
    pct_unique_rows = num_unique_rows / num_rows if num_rows else float("nan")
    pct_duplicated_rows = 1.0 - pct_unique_rows
    return Template(
        """
<table class="table table-hover table-responsive w-auto" >
<thead class="thead table-group-divider">
    <tr>
        <th>number of rows</th>
        <th>number of unique rows</th>
        <th>number of duplicated rows</th>
    </tr>
</thead>
<tbody class="tbody table-group-divider">
    <tr>
        <td {{num_style}}>{{num_rows}}</td>
        <td {{num_style}}>{{num_unique_rows}} ({{pct_unique_rows}}%)</td>
        <td {{num_style}}>{{num_duplicated_rows}} ({{pct_duplicated_rows}}%)</td>
    </tr>
    <tr class="table-group-divider"></tr>
</tbody>
</table>
"""
    ).render(
        {
            "num_style": 'style="text-align: right;"',
            "num_rows": f"{num_rows:,}",
            "num_unique_rows": f"{num_unique_rows:,}",
            "num_duplicated_rows": f"{num_duplicated_rows:,}",
            "pct_unique_rows": f"{100 * pct_unique_rows:.2f}",
            "pct_duplicated_rows": f"{100 * pct_duplicated_rows:.2f}",
        }
    )

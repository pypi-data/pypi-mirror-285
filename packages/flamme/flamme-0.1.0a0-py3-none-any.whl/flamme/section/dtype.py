r"""Contain the implementation of a section to analyze the data types of
each column."""

from __future__ import annotations

__all__ = ["DataTypeSection", "create_section_template", "create_table", "create_table_row"]

import copy
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


class DataTypeSection(BaseSection):
    r"""Implement a section that analyzes the data type of each column.

    Args:
        dtypes: The data type for each column.
        types: The types of the values in each
            column. A column can contain multiple types. The keys are
            the column names.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section import DataTypeSection
    >>> section = DataTypeSection(
    ...     dtypes={"float": pl.Float64(), "int": pl.Int64(), "str": pl.String()},
    ...     types={"float": {float}, "int": {int}, "str": {str, type(None)}},
    ... )
    >>> section
    DataTypeSection(
      (dtypes): {'float': Float64, 'int': Int64, 'str': String}
      (types): {'float': {<class 'float'>}, 'int': {<class 'int'>}, 'str': {...}}
    )
    >>> section.get_statistics()
    {'float': {<class 'float'>}, 'int': {<class 'int'>}, 'str': {<class 'NoneType'>, <class 'str'>}}

    ```
    """

    def __init__(self, dtypes: dict[str, pl.DataType], types: dict[str, set]) -> None:
        self._dtypes = dtypes
        self._types = types

        dtkeys = set(self._dtypes.keys())
        tkeys = set(self._types.keys())
        if dtkeys != tkeys:
            msg = (
                f"The keys of dtypes and types do not match:\n"
                f"({len(dtkeys)}): {dtkeys}\n"
                f"({len(tkeys)}): {tkeys}\n"
            )
            raise RuntimeError(msg)

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"dtypes": self._dtypes, "types": self._types}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def get_statistics(self) -> dict:
        return copy.deepcopy(self._types)

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "table": create_table(dtypes=self._dtypes, types=self._types),
            }
        )

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        logger.info("Rendering the data types report...")
        return render_html_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from flamme.section.dtype import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">
This section analyzes the values types for each column.

<ul>
  <li> <b>data type</b>: is the column data type </li>
  <li> <b>types</b>: are the real object types for the objects in the column.
  A column can contain multiple types. </li>
</ul>

{{table}}
"""


def create_table(dtypes: dict[str, pl.DataType], types: dict[str, set]) -> str:
    r"""Return a HTML table with the data types information.

    Args:
        dtypes: The data type for each column.
        types: The types of the values in each
            column. A column can contain multiple types. The keys are
            the column names.

    Returns:
        The generated HTML table.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.dtype import create_table_row
    >>> table = create_table(
    ...     dtypes={"float": pl.Float64(), "int": pl.Int64(), "str": pl.String()},
    ...     types={"float": {float}, "int": {int}, "str": {str, type(None)}},
    ... )

    ```
    """
    columns = sorted(types.keys())
    rows = "\n".join(
        [create_table_row(column=col, types=types[col], dtype=dtypes[col]) for col in columns]
    )
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>data type</th>
            <th>types</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": rows})


def create_table_row(column: str, dtype: pl.DataType, types: set[type]) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        dtype: The column data type.
        types: The types in th column.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from flamme.section.dtype import create_table_row
    >>> row = create_table_row(column="col", dtype=pl.Int64(), types={int})

    ```
    """
    types = sorted([str(t).replace("<", "&lt;").replace(">", "&gt;") for t in types])
    return Template(
        """<tr>
    <th>{{column}}</th>
    <td>{{dtype}}</td>
    <td>{{types}}</td>
</tr>"""
    ).render({"column": column, "dtype": dtype, "types": ", ".join(types)})

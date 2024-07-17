r"""Implement a section that generates a table of content."""

from __future__ import annotations

__all__ = ["TableOfContentSection"]

from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping

from flamme.section.base import BaseSection

if TYPE_CHECKING:
    from collections.abc import Sequence


class TableOfContentSection(BaseSection):
    r"""Implement a wrapper section that generates a table of content
    before the section.

    Args:
        section: The section.
        max_toc_depth: The maximum level to show in the
            table of content.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> import numpy as np
    >>> from flamme.section import TableOfContentSection, DuplicatedRowSection
    >>> section = TableOfContentSection(
    ...     DuplicatedRowSection(
    ...         frame=pl.DataFrame(
    ...             {
    ...                 "col1": [1.2, 4.2, 4.2, 2.2],
    ...                 "col2": [1, 1, 1, 1],
    ...                 "col3": [1, 2, 2, 2],
    ...             },
    ...             schema={"col1": pl.Float64, "col2": pl.Int64, "col3": pl.Int64},
    ...         )
    ...     )
    ... )
    >>> section
    TableOfContentSection(
      (section): DuplicatedRowSection(
          (frame): (4, 3)
          (columns): None
          (figsize): None
        )
      (max_toc_depth): 1
    )
    >>> section.get_statistics()
    {'num_rows': 4, 'num_unique_rows': 3}

    ```
    """

    def __init__(self, section: BaseSection, max_toc_depth: int = 1) -> None:
        self._section = section
        self._max_toc_depth = int(max_toc_depth)

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping({"section": self._section, "max_toc_depth": self._max_toc_depth})
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def get_statistics(self) -> dict:
        return self._section.get_statistics()

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        toc = self._section.render_html_toc(
            number=number, tags=tags, depth=0, max_depth=self._max_toc_depth
        )
        body = self._section.render_html_body(number=number, tags=tags, depth=depth)
        return f"{toc}\n\n{body}"

    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return self._section.render_html_toc(
            number=number, tags=tags, depth=depth, max_depth=max_depth
        )

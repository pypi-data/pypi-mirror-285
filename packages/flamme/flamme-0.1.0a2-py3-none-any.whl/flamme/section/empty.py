r"""Contain the implementation of an empty section."""

from __future__ import annotations

__all__ = ["EmptySection"]

from typing import TYPE_CHECKING

from flamme.section.base import BaseSection

if TYPE_CHECKING:
    from collections.abc import Sequence


class EmptySection(BaseSection):
    r"""Implement an empty section.

    This section is implemented to deal with missing columns or to skip
    some analyses.

    Example usage:

    ```pycon

    >>> from flamme.section import EmptySection
    >>> section = EmptySection()
    >>> section
    EmptySection()
    >>> section.get_statistics()
    {}

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(
        self,
        number: str = "",  # noqa: ARG002
        tags: Sequence[str] = (),  # noqa: ARG002
        depth: int = 0,  # noqa: ARG002
    ) -> str:
        return ""

    def render_html_toc(
        self,
        number: str = "",  # noqa: ARG002
        tags: Sequence[str] = (),  # noqa: ARG002
        depth: int = 0,  # noqa: ARG002
        max_depth: int = 1,  # noqa: ARG002
    ) -> str:
        return ""

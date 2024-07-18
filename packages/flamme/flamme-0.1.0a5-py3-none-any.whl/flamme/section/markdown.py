r"""Contain the implementation of a section to convert a markdown string
into HTML."""

from __future__ import annotations

__all__ = ["MarkdownSection", "create_section_template"]

import logging
from typing import TYPE_CHECKING

from jinja2 import Template

from flamme.section.base import BaseSection
from flamme.section.utils import (
    GO_TO_TOP,
    render_html_toc,
    tags2id,
    tags2title,
    valid_h_tag,
)
from flamme.utils.imports import check_markdown, is_markdown_available

if TYPE_CHECKING:
    from collections.abc import Sequence

if is_markdown_available():  # pragma: no cover
    import markdown

logger = logging.getLogger(__name__)


class MarkdownSection(BaseSection):
    r"""Implement a section that converts a markdown string into HTML.

    Args:
        desc: The markdown string to convert.

    Example usage:

    ```pycon

    >>> from flamme.section import MarkdownSection
    >>> section = MarkdownSection(desc="meow")
    >>> section
    MarkdownSection()
    >>> section.get_statistics()
    {}

    ```
    """

    def __init__(self, desc: str) -> None:
        check_markdown()
        self._desc = str(desc)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Rendering the markdown section...")
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "desc": markdown.markdown(self._desc),
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

    >>> from flamme.section.markdown import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">

{{desc}}
"""

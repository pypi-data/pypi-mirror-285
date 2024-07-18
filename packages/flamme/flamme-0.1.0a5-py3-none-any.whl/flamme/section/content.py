r"""Contain the implementation of a section that generates the given
custom content."""

from __future__ import annotations

__all__ = ["ContentSection", "create_section_template"]

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

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = logging.getLogger(__name__)


class ContentSection(BaseSection):
    r"""Implement a section that generates the given custom content.

    Args:
        content: The content to use in the HTML code.

    Example usage:

    ```pycon

    >>> from flamme.section import ContentSection
    >>> section = ContentSection(content="meow")
    >>> section
    ContentSection()
    >>> section.get_statistics()
    {}

    ```
    """

    def __init__(self, content: str) -> None:
        self._content = str(content)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def get_statistics(self) -> dict:
        return {}

    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Rendering the section with the custom content...")
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "content": self._content,
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

    >>> from flamme.section.content import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">

{{content}}

<p style="margin-top: 1rem;">
"""

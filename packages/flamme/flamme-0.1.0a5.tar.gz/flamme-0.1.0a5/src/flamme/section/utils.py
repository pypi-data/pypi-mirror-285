r"""Contain utility functions to generate sections."""

from __future__ import annotations

__all__ = [
    "GO_TO_TOP",
    "render_html_toc",
    "tags2id",
    "tags2title",
    "valid_h_tag",
]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

GO_TO_TOP = '<a href="#">Go to top</a>'


def tags2id(tags: Sequence[str]) -> str:
    r"""Convert a sequence of tags to a string that can be used as ID in
    a HTML file.

    Args:
        tags: The sequence of tags.

    Returns:
        The generated ID from the tags.
    """
    return "-".join(tags).replace(" ", "-").lower()


def tags2title(tags: Sequence[str]) -> str:
    r"""Convert a sequence of tags to a string that can be used as title.

    Args:
        tags: The sequence of tags.

    Returns:
        The generated title from the tags.
    """
    return " | ".join(tags[::-1])


def valid_h_tag(index: int) -> int:
    r"""Return a valid number of a h HTML tag.

    Args:
        index: The original value.

    Returns:
        A valid value.
    """
    return max(1, min(6, index))


def render_html_toc(
    number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
) -> str:
    r"""Return the HTML table of content (TOC) associated to the section.

    Args:
        number: The section number associated to the section.
        tags: The tags associated to the section.
        depth: The depth in the report.
        max_depth: The maximum depth to generate in the TOC.

    Returns:
        The HTML table of content associated to the section.
    """
    if depth >= max_depth:
        return ""
    tag = tags[-1] if tags else ""
    return f'<li><a href="#{tags2id(tags)}">{number} {tag}</a></li>'

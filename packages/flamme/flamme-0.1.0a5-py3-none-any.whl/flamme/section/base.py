r"""Contain the base class to implement a section."""

from __future__ import annotations

__all__ = ["BaseSection"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class BaseSection(ABC):
    r"""Define the base class to manage sections."""

    @abstractmethod
    def get_statistics(self) -> dict:
        r"""Return the statistics associated to the section.

        Returns:
            The statistics.
        """

    @abstractmethod
    def render_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        r"""Return the HTML body associated to the section.

        Args:
            number: The section number.
            tags: The tags associated to the section.
            depth: The depth in the report.

        Returns:
            The HTML body associated to the section.
        """

    @abstractmethod
    def render_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        r"""Return the HTML table of content (TOC) associated to the
        section.

        Args:
            number: The section number associated to the
                section.
            tags: The tags associated to the section.
            depth: The depth in the report.
            max_depth: The maximum depth to generate in the TOC.

        Returns:
            The HTML table of content associated to the section.
        """

r"""Contain utility functions to manage paths."""

from __future__ import annotations

__all__ = ["find_files", "find_parquet_files", "human_file_size"]

from typing import TYPE_CHECKING

from coola.utils.path import sanitize_path

from flamme.utils.format import human_byte

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def human_file_size(path: Path | str, decimal: int = 2) -> str:
    r"""Get a human-readable representation of a file size.

    Args:
        path: The path to the file.
        decimal: The number of decimal digits.

    Returns:
        The file size in a human-readable format.

    Example usage:

    ```pycon

    >>> from flamme.utils.path import human_file_size
    >>> human_file_size("README.md")
    '...B'

    ```
    """
    return human_byte(size=sanitize_path(path).stat().st_size, decimal=decimal)


def find_files(
    path: Path | str, filter_fn: Callable[[Path], bool], recursive: bool = True
) -> list[Path]:
    r"""Find the path of all the tar files in a given path.

    This function does not check if a path is a symbolic link so be
    careful if you are using a path with symbolic links.

    Args:
        path: The path where to look for the parquet files.
        filter_fn: The path filtering function. The function
            should return ``True`` for the path to find, and
            ``False`` otherwise.
        recursive: Indicate if it should also check the sub-folders.

    Returns:
        The tuple of path of parquet files.

    Example usage:

    ```pycon

    >>> from pathlib import Path
    >>> from flamme.utils.path import find_files
    >>> find_files(Path("something"), filter_fn=lambda path: path.name.endswith(".txt"))
    [...]

    ```
    """
    path = sanitize_path(path)
    paths = [path] if path.is_file() else path.glob("**/*" if recursive else "*")
    return list(filter(filter_fn, [p for p in paths if p.is_file()]))


def find_parquet_files(path: Path | str, recursive: bool = True) -> list[Path]:
    r"""Find the path of all the parquet files in a given path.

    This function does not check if a path is a symbolic link so be
    careful if you are using a path with symbolic links.

    Args:
        path: The path where to look for the parquet files.
        recursive: Specifies if it should also check the sub-folders.

    Returns:
        The list of parquet files.

    Example usage:

    ```pycon

    >>> from pathlib import Path
    >>> from flamme.utils.path import find_parquet_files
    >>> find_parquet_files(Path("something"))
    [...]

    ```
    """
    return find_files(
        path=path, filter_fn=lambda path: path.name.endswith(".parquet"), recursive=recursive
    )

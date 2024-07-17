r"""Implement some utility functions to manage optional dependencies."""

from __future__ import annotations

__all__ = [
    "check_clickhouse_connect",
    "check_colorlog",
    "check_markdown",
    "clickhouse_connect_available",
    "colorlog_available",
    "is_clickhouse_connect_available",
    "is_colorlog_available",
    "is_markdown_available",
    "markdown_available",
]

from typing import TYPE_CHECKING, Any

from coola.utils.imports import decorator_package_available, package_available

if TYPE_CHECKING:
    from collections.abc import Callable


##############################
#     clickhouse_connect     #
##############################


def is_clickhouse_connect_available() -> bool:
    r"""Indicate if the ``clickhouse_connect`` package is installed or
    not.

    Returns:
        ``True`` if ``clickhouse_connect`` is available otherwise
            ``False``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import is_clickhouse_connect_available
    >>> is_clickhouse_connect_available()

    ```
    """
    return package_available("clickhouse_connect")


def check_clickhouse_connect() -> None:
    r"""Check if the ``clickhouse_connect`` package is installed.

    Raises:
        RuntimeError: if the ``clickhouse_connect`` package is not
            installed.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import check_clickhouse_connect
    >>> check_clickhouse_connect()

    ```
    """
    if not is_clickhouse_connect_available():
        msg = (
            "`clickhouse_connect` package is required but not installed. "
            "You can install `clickhouse_connect` package with the command:\n\n"
            "pip install clickhouse-connect\n"
        )
        raise RuntimeError(msg)


def clickhouse_connect_available(fn: Callable[..., Any]) -> Callable[..., Any]:
    r"""Implement a decorator to execute a function only if
    ``clickhouse_connect`` package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``clickhouse_connect`` package is
            installed, otherwise ``None``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import clickhouse_connect_available
    >>> @clickhouse_connect_available
    ... def my_function(n: int = 0) -> int:
    ...     return 42 + n
    ...
    >>> my_function()

    ```
    """
    return decorator_package_available(fn, is_clickhouse_connect_available)


####################
#     colorlog     #
####################


def is_colorlog_available() -> bool:
    r"""Indicate if the ``colorlog`` package is installed or not.

    Returns:
        ``True`` if ``colorlog`` is available otherwise
            ``False``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import is_colorlog_available
    >>> is_colorlog_available()

    ```
    """
    return package_available("colorlog")


def check_colorlog() -> None:
    r"""Check if the ``colorlog`` package is installed.

    Raises:
        RuntimeError: if the ``colorlog`` package is not
            installed.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import check_colorlog
    >>> check_colorlog()

    ```
    """
    if not is_colorlog_available():
        msg = (
            "`colorlog` package is required but not installed. "
            "You can install `colorlog` package with the command:\n\n"
            "pip install colorlog\n"
        )
        raise RuntimeError(msg)


def colorlog_available(fn: Callable[..., Any]) -> Callable[..., Any]:
    r"""Implement a decorator to execute a function only if ``colorlog``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``colorlog`` package is
            installed, otherwise ``None``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import colorlog_available
    >>> @colorlog_available
    ... def my_function(n: int = 0) -> int:
    ...     return 42 + n
    ...
    >>> my_function()

    ```
    """
    return decorator_package_available(fn, is_colorlog_available)


####################
#     markdown     #
####################


def is_markdown_available() -> bool:
    r"""Indicate if the ``markdown`` package is installed or not.

    Returns:
        ``True`` if ``markdown`` is available otherwise
            ``False``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import is_markdown_available
    >>> is_markdown_available()

    ```
    """
    return package_available("markdown")


def check_markdown() -> None:
    r"""Check if the ``markdown`` package is installed.

    Raises:
        RuntimeError: if the ``markdown`` package is not
            installed.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import check_markdown
    >>> check_markdown()

    ```
    """
    if not is_markdown_available():
        msg = (
            "`markdown` package is required but not installed. "
            "You can install `markdown` package with the command:\n\n"
            "pip install markdown\n"
        )
        raise RuntimeError(msg)


def markdown_available(fn: Callable[..., Any]) -> Callable[..., Any]:
    r"""Implement a decorator to execute a function only if ``markdown``
    package is installed.

    Args:
        fn: The function to execute.

    Returns:
        A wrapper around ``fn`` if ``markdown`` package is
            installed, otherwise ``None``.

    Example usage:

    ```pycon

    >>> from flamme.utils.imports import markdown_available
    >>> @markdown_available
    ... def my_function(n: int = 0) -> int:
    ...     return 42 + n
    ...
    >>> my_function()

    ```
    """
    return decorator_package_available(fn, is_markdown_available)

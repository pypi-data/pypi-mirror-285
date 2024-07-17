r"""Contain some clickhouse utility functions."""

from __future__ import annotations

__all__ = ["get_table_schema"]


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flamme.utils.imports import is_clickhouse_connect_available

    if is_clickhouse_connect_available():  # pragma: no cover
        from clickhouse_connect.driver.client import Client
    import pyarrow as pa


def get_table_schema(client: Client, table: str) -> pa.Schema:
    r"""Return the table schema.

    Args:
        client: The clickhouse client.
        table: The table.

    Returns:
        The table schema.
    """
    return client.query_arrow(query=f"select top 1 * from {table}").schema  # noqa: S608

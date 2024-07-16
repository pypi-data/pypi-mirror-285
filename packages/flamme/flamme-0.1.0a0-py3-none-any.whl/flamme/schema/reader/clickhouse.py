r"""Contain the implementation of a simple ingestor."""

from __future__ import annotations

__all__ = ["ClickHouseSchemaReader"]

import logging
from typing import TYPE_CHECKING

from flamme.schema.reader.base import BaseSchemaReader
from flamme.utils import setup_object

if TYPE_CHECKING:
    import pyarrow as pa

    from flamme.utils.imports import is_clickhouse_connect_available

    if is_clickhouse_connect_available():
        import clickhouse_connect

logger = logging.getLogger(__name__)


class ClickHouseSchemaReader(BaseSchemaReader):
    r"""Implement a simple DataFrame ingestor.

    Args:
        query: The query to get the data.
        client: The clickhouse client or its configuration.
            Please check the documentation of
            ``clickhouse_connect.get_client`` to get more information.

    Example usage:

    ```pycon

    >>> from flamme.schema.reader import ClickHouseSchemaReader
    >>> client = clickhouse_connect.get_client()  # doctest: +SKIP
    >>> reader = ClickHouseSchemaReader(query="", client=client)  # doctest: +SKIP
    >>> schema = reader.read()  # doctest: +SKIP

    ```
    """

    def __init__(self, query: str, client: clickhouse_connect.driver.Client | dict) -> None:
        self._query = str(query)
        self._client: clickhouse_connect.driver.Client = setup_object(client)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def read(self) -> pa.Schema:
        logger.info(
            f"reading schema from clickhouse using the following query... \n\n"
            "---------------------------------------------------------------------------------\n"
            f"{self._query}\n"
            "---------------------------------------------------------------------------------\n\n"
        )
        return self._client.query_arrow(query=self._query).schema

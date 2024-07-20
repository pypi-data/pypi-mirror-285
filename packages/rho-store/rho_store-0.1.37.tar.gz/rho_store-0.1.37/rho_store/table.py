from typing import Callable

import pandas as pd

from .config import init_config
from .types import StoreDfCommand


class Table:
    def __init__(
        self,
        table_id: str,
        workspace_id: str,
        name: str = "",
        data: pd.DataFrame = None,
        fetch_data: Callable[[str, int], pd.DataFrame] = None,
        store_data: Callable[[StoreDfCommand], None] = None,
    ):
        self.table_id = table_id
        self.workspace_id = workspace_id
        self.name = name
        self._data = data
        self._fetch_data = fetch_data
        self._store_data = store_data
        self._config = init_config()

    def __str__(self) -> str:
        return f'<Table id="{self.table_id}" name="{self.name}" url="{self.client_url}">'

    def __repr__(self) -> str:
        return f'<Table id="{self.table_id}" name="{self.name}" url="{self.client_url}">'

    @property
    def client_url(self) -> str:
        return f"{self._config.CLIENT_URL}/app/tables/{self.table_id}?wid={self.workspace_id}"

    @property
    def data(self, refresh: bool = False) -> pd.DataFrame:
        if self._data is None or refresh is True:
            self._data = self.fetch_data()
        return self._data

    def fetch_data(self, version: int = None) -> pd.DataFrame:
        return self._fetch_data(self.table_id, version)

    def append(self, data: pd.DataFrame) -> None:
        command = StoreDfCommand(data=data, table_id=self.table_id, strategy="APPEND", run_async=True)
        self._store_data(command)
        self._clear_cache()

    def replace(self, data: pd.DataFrame) -> None:
        command = StoreDfCommand(data=data, table_id=self.table_id, strategy="REPLACE", run_async=True)
        self._store_data(command)
        self._clear_cache()

    def merge(self, data: pd.DataFrame, column: str) -> None:
        command = StoreDfCommand(
            data=data, table_id=self.table_id, strategy="MERGE", merge_options={"column": column}, run_async=True
        )
        self._store_data(command)
        self._clear_cache()

    def _clear_cache(self) -> None:
        self._data = None


__all__ = ["Table"]

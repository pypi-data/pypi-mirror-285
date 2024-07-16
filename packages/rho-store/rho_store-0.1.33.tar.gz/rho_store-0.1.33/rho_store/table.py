from typing import Callable

import pandas as pd

from .config import init_config


class Table:
    def __init__(
        self,
        table_id: str,
        workspace_id: str,
        name: str = "",
        data: pd.DataFrame = None,
        fetch_data: Callable[[str, int], pd.DataFrame] = None,
    ):
        self.table_id = table_id
        self.workspace_id = workspace_id
        self.name = name
        self._data = data
        self._fetch_data = fetch_data
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


__all__ = ["Table"]

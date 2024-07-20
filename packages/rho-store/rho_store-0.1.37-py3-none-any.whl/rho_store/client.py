from typing import Optional

import pandas as pd

from .adapters import RhoApiGraphqlAdapter, UploadFileHttpAdapter, DataTransportRestAdapter, UptimeCheckHttpAdapter
from .config import init_config
from .exceptions import InvalidArgument
from .table import Table
from .types import TableDataResult, StoreDfCommand


class RhoClient:
    DEFAULT_STRATEGY = "NEW_TABLE"

    def __init__(self, api_key: str):
        config = init_config()
        self._file_upload_port = UploadFileHttpAdapter()
        self._api_port = RhoApiGraphqlAdapter(base_url=config.GRAPHQL_URL, api_key=api_key, client_id=config.CLIENT_ID)
        self._data_transport_port = DataTransportRestAdapter(
            base_url=config.API_URL, api_key=api_key, client_id=config.CLIENT_ID
        )
        self._uptime_check = UptimeCheckHttpAdapter(url=config.uptime_check_url, client_id=config.CLIENT_ID)
        # Check if the server is up
        self._uptime_check.check(timeout=0.5)

    def new_table(self, name: str) -> dict:
        table = self._api_port.create_table(name)
        return table

    def _store_df(self, command: StoreDfCommand) -> Table:
        return self.store_df(
            command.data,
            name=command.name,
            table_id=command.table_id,
            strategy=command.strategy,
            merge_options=command.merge_options,
            run_async=command.run_async,
        )

    def store_df(
        self,
        data: pd.DataFrame,
        name: str = None,
        table_id: str = None,
        strategy: str = None,
        merge_options: Optional[dict] = None,
        run_async: bool = True,
    ) -> Table:
        strategy = strategy.upper() if strategy else self.DEFAULT_STRATEGY
        self.validate_store_df_strategy(strategy, table_id, merge_options)

        # Wait for the server to be ready
        self._uptime_check.wait_until_ready()

        url, file_id = self._api_port.get_signed_url()
        self._file_upload_port.upload_dataframe(url, data)

        if table_id is None:
            if name is None:
                name = "New table"
            created_table = self._api_port.create_table(name)
            table_id = created_table["id"]

        table = self._api_port.process_file(
            file_id, table_id, strategy, merge_options=merge_options, run_async=run_async
        )
        workspace_id = table["workspaceId"]
        return Table(table_id=table["id"], workspace_id=workspace_id, data=data)

    @staticmethod
    def validate_store_df_strategy(
        strategy: str, table_id: Optional[str] = None, merge_options: Optional[dict] = None
    ) -> None:
        valid_strategies = {"NEW_TABLE", "NEW_VERSION", "APPEND", "MERGE", "REPLACE"}
        if strategy not in valid_strategies:
            raise InvalidArgument(f"Invalid strategy: {strategy}")

        if strategy != "NEW_TABLE" and table_id is None:
            # if not "new_table" -> table_id is required
            raise InvalidArgument(f"Cannot perform strategy {strategy} without a table_id")

        if strategy == "MERGE":
            # if "merge" -> merge_options is required
            merge_options = merge_options or {}
            if merge_options.get("column") is None:
                raise InvalidArgument(f"Cannot perform strategy {strategy} without valid merge_options")

    def store_data(self, data: list[dict]) -> Table:
        df = pd.DataFrame(data)
        return self.store_df(df)

    def list_tables(self) -> list[Table]:
        tables = self._api_port.list_tables()
        return [
            Table(
                table_id=table["id"],
                name=table["name"],
                workspace_id=table["workspaceId"],
                data=None,
                fetch_data=self.get_df,
                store_data=self._store_df,
            )
            for table in tables
        ]

    def get_table(self, table_id: str, version: Optional[int] = None) -> Table:
        table = self._api_port.get_table(table_id)
        table_data = self._get_table_data(table_id, version)
        parsed_data = pd.DataFrame(data=table_data.rows, columns=table_data.columns)
        df = self._remove_system_columns(parsed_data)
        return Table(
            table_id=table_id, name=table["name"], workspace_id=table_data.workspace_id, data=df, fetch_data=self.get_df
        )

    def get_df(self, table_id: str, version: Optional[int] = None) -> pd.DataFrame:
        result = self._get_table_data(table_id, version)
        parsed_data = pd.DataFrame(data=result.rows, columns=result.columns)
        df = self._remove_system_columns(parsed_data)
        return df

    def get_data(self, table_id: str, version: Optional[int] = None) -> list[dict]:
        # TODO: Remove system columns?
        table_data = self._get_table_data(table_id, version)
        return table_data.to_list()

    def _get_table_data(self, table_id: str, version: Optional[int] = None) -> TableDataResult:
        # Wait for the server to be ready
        self._uptime_check.wait_until_ready()

        result = self._data_transport_port.get_table_data(table_id, version)
        return result

    @staticmethod
    def _remove_system_columns(df: pd.DataFrame) -> pd.DataFrame:
        system_columns = ["_id", "_version", "_created_at"]
        df.drop(columns=system_columns, inplace=True, errors="ignore")
        return df


__all__ = ["RhoClient"]

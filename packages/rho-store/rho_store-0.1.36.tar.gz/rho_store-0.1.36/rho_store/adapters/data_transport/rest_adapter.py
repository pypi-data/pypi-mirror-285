import logging
from typing import Optional

import orjson
import requests
from cachetools import TTLCache, cached

from ...exceptions import FailedToGetData, RhoServerTimeout
from ...ports import DataTransportPort
from ...types import TableDataResult

logger = logging.getLogger(__name__)


class DataTransportRestAdapter(DataTransportPort):
    REQUEST_TIMEOUT = 15.0

    def __init__(self, base_url: str, api_key: str, client_id: str = "python-sdk"):
        self.base_url = base_url
        self.api_key = api_key
        self.client_id = client_id
        self.session = requests.Session()

    def get_table_data(self, table_id: str, version: Optional[int] = None) -> TableDataResult:
        return self._get_table_data(table_id, version)

    @cached(cache=TTLCache(maxsize=10, ttl=30))
    def _get_table_data(self, table_id: str, version: Optional[int] = None) -> TableDataResult:
        url = self.get_url_for_table(table_id)
        params = {}
        if version:
            params["version"] = version

        try:
            response = self.session.get(url, headers=self.get_headers(), params=params, timeout=self.REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout as e:
            raise RhoServerTimeout("Timeout while fetching data") from e
        except requests.exceptions.RequestException as e:
            raise FailedToGetData("Failed to make request") from e

        response_data = orjson.loads(response.content)

        if not response.ok:
            raise FailedToGetData(response_data.get("error"))

        if data := response_data.get("data"):
            return TableDataResult(
                table_id=table_id,
                workspace_id=data.get("workspaceId"),
                columns=data.get("columns", []),
                rows=data.get("rows", []),
            )

        logger.warning("Received response: %s", response_data)
        raise FailedToGetData(response_data.get("error"))

    def get_url_for_table(self, table_id: str) -> str:
        return f"{self.base_url}/v1/tables/{table_id}/data"

    def get_headers(self) -> dict:
        return {"Content-Type": "application/json", "X-Api-Key": self.api_key, "X-Client-ID": self.client_id}


__all__ = ["DataTransportRestAdapter"]

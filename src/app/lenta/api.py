import json as json_
from http import HTTPStatus
from typing import Optional, Union

import aiohttp

from lenta.cache.base import BaseCache, create_key_by_args
from lenta.exeptions import LentaBaseException

LENTA_BASE_URL = "https://lenta.com"
FAKE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) " \
                  "CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1"


class ApiServer:
    def __init__(self, base: str):
        self.base = f"{base}/api/{{method}}"

    def api_url(self, method: str) -> str:
        """
        Формирвоание URL для метода API
        :param method: Метод
        :return: URL
        """
        return self.base.format(method=method)


class ApiMethods:
    GET_CITIES = "v1/cities"
    GET_STORES = "v1/stores"
    GET_STORE = "v1/stores/{store_id}"
    GET_CITY_STORES = "v1/cities/{city_id}/stores"
    STORE_SKUS = "v1/stores/{store_id}/skus"
    STORE_SKUS_LIST = "v1/stores/{store_id}/skusList"
    GET_STORE_SKUS = "v1/stores/{store_id}/skus/{code}"
    GET_CATALOG = "v2/stores/{store_id}/catalog"


class ApiService:

    def __init__(self, server: Optional[ApiServer] = None,
                 session: Optional[aiohttp.ClientSession] = None,
                 cache: Optional[BaseCache] = None):
        if session is None:
            session = aiohttp.ClientSession(
                headers={
                    "user-agent": FAKE_USER_AGENT
                }
            )

        if server is None:
            server = ApiServer(LENTA_BASE_URL)

        self._server = server
        self._session = session
        self._cache = cache

    async def api_request(
            self,
            http_method: str,
            api_method: str,
            params: Optional[dict] = None,
            json: Optional[dict] = None,
            cache_time: int = 0,
    ):
        if params is None:
            params = {}
        if json is None:
            json = {}

        url = self._server.api_url(api_method)
        return await self.raw_request(
            url,
            http_method,
            params,
            json,
            cache_time,
        )

    async def raw_request(
            self,
            url: str,
            method: str,
            params: dict,
            json: dict,
            cache_time: int,
    ) -> Union[list, dict]:

        cache_key = create_key_by_args(url, method, **params, **json)
        response_from_cache = await self._cache.get(cache_key)
        if response_from_cache:
            return response_from_cache

        response = await self._session.request(
            method,
            url,
            json=json,
            params=params,
        )

        response_json = self.check_result(response.status, await response.text())

        if cache_time:
            await self._cache.set(cache_key, response_json, cache_time)

        return response_json

    @classmethod
    def check_result(cls, status_code: int, body: str) -> dict:
        try:
            result_json = json_.loads(body)
        except ValueError:
            result_json = {}

        if status_code == HTTPStatus.OK:
            return result_json

        if status_code >= 500:
            message = "Server error"
        else:
            message = result_json.get("message")

        raise LentaBaseException(
            message=message,
            error_code=status_code,
        )

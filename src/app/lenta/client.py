import asyncio
import json
from typing import Optional, Union

import aiohttp

from . import models

LENTA_BASE_URL = "https://lenta.com/api"


class LentaClient:

    def __init__(self,
                 loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None,
                 base_url: str = LENTA_BASE_URL,
                 ):
        self._main_loop = loop
        self._session = self.get_new_session()
        self._base_url = base_url

    def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            loop=self._main_loop,
            json_serialize=json.dumps,
        )

    async def make_request(self, endpoint: str,
                           method: str = "GET",
                           params: Optional[dict] = None,
                           data: Optional[dict] = None) -> Union[list[dict], dict]:
        """
        Формирование запроса
        :param endpoint: Url метода
        :param method: Метод запроса
        :param params: Url параметры
        :param data: Тело запроса
        :return:
        """
        url = self.build_url(endpoint)
        async with self._session.request(method, url, json=data, params=params) as response:
            return await response.json()

    def build_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    async def get_cities(self) -> list[models.City]:
        """
        Получение списка городов, в которых есть магазины Ленты
        :return: Список городов
        """
        result = await self.make_request("/v1/cities")
        return [models.City(**city) for city in result]

    async def get_stores(self) -> list[models.Store]:
        """
        Получение списка магазинов Ленты
        :return:  Список магазинов
        """
        result = await self.make_request("/v1/stores")
        return [models.Store(**store) for store in result]

    async def get_city_stores(self, city_id: str) -> list[models.Store]:
        """
        Получение списка магазинов Лента для города
        :param city_id: Идентификатор города
        :return: Список магазинов для города
        """
        result = await self.make_request(f"/v1/cities/{city_id}/stores")
        return [models.Store(**store) for store in result]

    async def search_skus_in_store(
            self, store_id: str, search_value: Optional[str] = None, limit: int = 10, offset: int = 0,
            max_price: Optional[float] = None, min_price: Optional[float] = None, sorting: Optional[str] = None,
            only_discounts: bool = False
    ) -> list[models.BaseSku]:
        """
        Поиск товара в магазине
        :param store_id: Идентификатор магазина
        :param limit: Кол-во выбираемых элементов
        :param offset: Сдвиг выбираемых элементов
        :param max_price: Максимальная цена
        :param min_price: Минимальная цена
        :param sorting: Поле сортировки
        :param only_discounts: Только товары со скидками
        :param search_value: Название товара для поиска
        :return: Найденные товары
        """
        payload = {
            "searchValue": search_value,
            "limit": limit,
            "offset": offset,
            "maxPrice": max_price,
            "minPrice": min_price,
            "sorting": sorting,
            "onlyDiscounts": only_discounts,
        }
        result = await self.make_request(f"/v1/stores/{store_id}/skus", "POST", data=payload)
        return [models.BaseSku(**sku) for sku in result["skus"]]

    async def get_store(self, store_id: str) -> models.Store:
        """
        Получение информации о магазине
        :param store_id: Идентификатор магазина
        :return: Магазин
        """

        result = await self.make_request(f"/v1/stores/{store_id}")
        return models.Store(**result)

    async def get_sku_in_store_by_barcode(self, store_id: str, barcode: str) -> models.BaseSku:
        """
        Получение информации о товаре по коду
        :param store_id:
        :param barcode:
        :return: Товар
        """

        result = await self.make_request(f"/v1/stores/{store_id}/skus", params={
            "barcode": barcode,
        })
        return models.BaseSku(**result)

    async def get_store_skus_by_ids(self, store_id: str, sku_ids: list[str]) -> list[models.BaseSku]:
        """
        Получение товаров магазина по иденификаторам товаров
        :param store_id: Идетификатор магазина
        :param sku_ids: Идентификаторы товаров
        :return: Список товаров
        """
        payload = {
            "skuCodes": sku_ids
        }
        result = await self.make_request(f"/v1/stores/{store_id}/skuslist", "POST", data=payload)
        return [models.BaseSku(**sku) for sku in result]

    async def get_sku(self, store_id: str, code: str) -> models.BaseSku:
        """
        Получение товара магазина по идентификатору
        :param store_id: Идентификатор магазина
        :param code: Код товара
        :return: Товар
        """

        result = await self.make_request(f"/v1/stores/{store_id}/skus/{code}")
        return models.BaseSku(**result)

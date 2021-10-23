import asyncio
import json
from typing import Optional, Union

import aiohttp

from . import models
from .cache.base import BaseCache, create_key_by_args
from .consts import DAY, HOUR

LENTA_BASE_URL = "https://lenta.com/api"
FAKE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) " \
                  "CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1"


class LentaClient:

    def __init__(self,
                 loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None,
                 base_url: str = LENTA_BASE_URL,
                 cache_storage: Optional[BaseCache] = None
                 ):
        self._main_loop = loop
        self._session = self.get_new_session()
        self._base_url = base_url
        self.cache_storage = cache_storage

    def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            loop=self._main_loop,
            json_serialize=json.dumps,
            headers={
                "user-agent": FAKE_USER_AGENT,
            }
        )

    async def make_request(
            self, endpoint: str,
            method: str = "GET",
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            ttl: int = 0,
    ) -> Union[list[dict], dict]:
        """
        Формирование запроса
        :param endpoint: Url метода
        :param method: Метод запроса
        :param params: Url параметры
        :param data: Тело запроса
        :param ttl: Время хранения в кэше (Если 0, то кэш не используется)
        :return:
        """
        data = {} if data is None else data
        params = {} if params is None else params

        url = self.build_url(endpoint)

        # Попытка получить результат из кэша
        key = create_key_by_args(url, **data, **params)
        result = await self._get_from_cache(key)
        if result is not None:
            return result

        async with self._session.request(method, url, json=data, params=params) as response:
            result = await response.json()

            # Сохранение значений в кэш при необходимости
            if ttl > 0 and method == "GET":
                await self._set_to_cache(key, result, ttl)
            return result

    def build_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    async def _get_from_cache(self, key: str) -> Optional[Union[list, dict]]:
        """
        Обёртка для получения значения их кэша

        :param key: Ключ
        :return: Значение из кэша
        """
        return await self.cache_storage.get(key) if self.cache_storage else None

    async def _set_to_cache(self, key: str, value: Union[list, dict, None], ttl: int) -> None:
        """
        Обёртка для установки значения в кэш
        :param key: Ключ
        :param value: Значение
        :param ttl: Время жизни
        :return:
        """
        if self.cache_storage:
            await self.cache_storage.set(key, value, ttl)

    async def get_cities(self) -> list[models.City]:
        """
        Получение списка городов, в которых есть магазины Ленты
        :return: Список городов
        """
        result = await self.make_request("/v1/cities", ttl=DAY)
        return [models.City(**city) for city in result]

    async def get_stores(self) -> list[models.Store]:
        """
        Получение списка магазинов Ленты
        :return:  Список магазинов
        """
        result = await self.make_request("/v1/stores", ttl=DAY)
        return [models.Store(**store) for store in result]

    async def get_city_stores(self, city_id: str) -> list[models.Store]:
        """
        Получение списка магазинов Лента для города
        :param city_id: Идентификатор города
        :return: Список магазинов для города
        """
        result = await self.make_request(f"/v1/cities/{city_id}/stores", ttl=DAY)
        return [models.Store(**store) for store in result]

    async def search_skus_in_store(
            self, store_id: str, search_value: Optional[str] = None, limit: int = 10, offset: int = 0,
            max_price: Optional[float] = None, min_price: Optional[float] = None, sorting: Optional[str] = None,
            only_discounts: bool = False, node_code: Optional[str] = None
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
        :param node_code: Код категории
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
            "nodeCode": node_code,
        }
        result = await self.make_request(f"/v1/stores/{store_id}/skus", "POST", data=payload)
        return [models.BaseSku(**sku) for sku in result["skus"]]

    async def get_store(self, store_id: str) -> models.Store:
        """
        Получение информации о магазине
        :param store_id: Идентификатор магазина
        :return: Магазин
        """

        result = await self.make_request(f"/v1/stores/{store_id}", ttl=DAY)
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

    async def get_catalog(self, store_id: str) -> models.Catalog:
        """
        Получение каталога для магазина
        :param store_id: Идентификатор магазина
        :return: Каталог магазина
        """

        result = await self.make_request(f"/v2/stores/{store_id}/catalog", ttl=HOUR)
        return models.Catalog(**result)

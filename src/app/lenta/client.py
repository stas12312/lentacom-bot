import asyncio
from typing import Optional, Union

from . import models
from .api import ApiService, ApiMethods
from .cache.base import BaseCache
from .consts import DAY, HOUR, MINUTE

LENTA_BASE_URL = "https://lenta.com/api"
FAKE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) " \
                  "CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1"


class LentaClient:

    def __init__(
            self,
            loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None,
            base_url: str = LENTA_BASE_URL,
            cache_storage: Optional[BaseCache] = None,
            api_service: Optional[ApiService] = None,
    ):
        self._main_loop = loop
        self._base_url = base_url
        if api_service is None:
            api_service = ApiService(cache=cache_storage)

        self._api_service = api_service

    async def request(
            self,
            api_method: str,
            http_method: str,
            params: Optional[dict] = None,
            json: Optional[dict] = None,
            cache_time: int = 0.
    ) -> Union[dict, list]:
        """
        Выполнение запроса
        :param api_method:
        :param http_method:
        :param params:
        :param json:
        :param cache_time:
        :return:
        """
        return await self._api_service.api_request(
            http_method,
            api_method,
            params,
            json,
            cache_time,
        )

    async def get_cities(self) -> list[models.City]:
        """
        Получение списка городов, в которых есть магазины Ленты
        :return: Список городов
        """
        result = await self.request(
            ApiMethods.GET_CITIES,
            "GET",
            cache_time=DAY
        )
        return [models.City(**city) for city in result]

    async def get_stores(self) -> list[models.Store]:
        """
        Получение списка магазинов Ленты
        :return:  Список магазинов
        """
        result = await self.request(
            ApiMethods.GET_STORES,
            "GET",
            cache_time=DAY
        )
        return [models.Store(**store) for store in result]

    async def get_city_stores(self, city_id: str) -> list[models.Store]:
        """
        Получение списка магазинов Лента для города
        :param city_id: Идентификатор города
        :return: Список магазинов для города
        """
        result = await self.request(
            ApiMethods.GET_CITY_STORES.format(city_id=city_id),
            "GET",
            cache_time=DAY
        )
        return [models.Store(**store) for store in result]

    async def search_skus_in_store(
            self, store_id: str, search_value: Optional[str] = None, limit: int = 10, offset: int = 0,
            max_price: Optional[float] = None, min_price: Optional[float] = None, sorting: Optional[str] = None,
            only_discounts: bool = False, node_code: Optional[str] = None,
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
        result = await self.request(
            ApiMethods.STORE_SKUS.format(store_id=store_id),
            "POST",
            json=payload,
        )
        return [models.BaseSku(**sku) for sku in result["skus"]]

    async def get_store(self, store_id: str) -> models.Store:
        """
        Получение информации о магазине
        :param store_id: Идентификатор магазина
        :return: Магазин
        """

        result = await self.request(
            ApiMethods.GET_STORE.format(store_id=store_id),
            "GET",
            cache_time=DAY
        )
        return models.Store(**result)

    async def get_sku_in_store_by_barcode(self, store_id: str, barcode: str) -> models.BaseSku:
        """
        Получение информации о товаре по коду
        :param store_id:
        :param barcode:
        :return: Товар
        """
        result = await self.request(
            ApiMethods.STORE_SKUS.format(store_id=store_id),
            "GET",
            params={
                "barcode": barcode,
            },
            cache_time=HOUR
        )
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
        result = await self.request(
            f"/v1/stores/{store_id}/skuslist",
            "POST",
            json=payload,
            cache_time=MINUTE * 5
        )
        return [models.BaseSku(**sku) for sku in result]

    async def get_sku(self, store_id: str, code: str) -> models.BaseSku:
        """
        Получение товара магазина по идентификатору
        :param store_id: Идентификатор магазина
        :param code: Код товара
        :return: Товар
        """

        result = await self.request(
            ApiMethods.GET_STORE_SKUS.format(store_id=store_id, code=code),
            "GET",
            cache_time=MINUTE * 5,
        )
        return models.BaseSku(**result)

    async def get_catalog(self, store_id: str) -> models.Catalog:
        """
        Получение каталога для магазина
        :param store_id: Идентификатор магазина
        :return: Каталог магазина
        """

        result = await self.request(
            ApiMethods.GET_CATALOG.format(store_id=store_id),
            "GET",
            cache_time=HOUR,
        )
        return models.Catalog(**result)

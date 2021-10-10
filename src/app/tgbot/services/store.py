from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lenta.client import LentaClient
from lenta.models import Store, City
from tgbot.callbacks.profile import city_cb, store_cb
from tgbot.services.utils import distance_between_points


async def get_city_by_name(city_name: str, lenta_client: LentaClient) -> Optional[City]:
    """
    Получение города по названию
    :param city_name:
    :param lenta_client:
    :return:
    """

    all_cities = await lenta_client.get_cities()

    for city in all_cities:
        if city.name == city_name:
            return city
    return None


async def get_inline_keyboard_for_cities(lenta_client: LentaClient) -> InlineKeyboardMarkup:
    """
    Получение инлайн клавиатуры для списка городов
    :return:
    """
    all_cities = await lenta_client.get_cities()
    all_cities = sorted(all_cities, key=lambda c: c.name)

    return InlineKeyboardMarkup(row_width=2).add(
        *[InlineKeyboardButton(city.name, callback_data=city_cb.new(city_id=city.id)) for city in all_cities]
    )


async def get_inline_keyboard_for_city_stores(lenta_client: LentaClient, city_id: str) -> InlineKeyboardMarkup:
    """
    Получение инлайн клавиатуры для списка магазинов
    :param lenta_client:
    :param city_id:
    :return:
    """
    city_stores = await lenta_client.get_city_stores(city_id)
    city_stores = sorted(city_stores, key=lambda s: s.name)

    return InlineKeyboardMarkup(row_width=2).add(
        *[InlineKeyboardButton(store.name, callback_data=store_cb.new(store_id=store.id)) for store in city_stores]
    )


async def get_store_by_coodrinites(lenta_client: LentaClient, latitude: float, longitude: float) -> Store:
    """Поиск ближайшего магазина Ленты"""
    cities = await lenta_client.get_cities()
    cities = sorted(cities, key=lambda c: distance_between_points(latitude, longitude, c.lat, c.long))
    nearest_city = cities[0]
    city_stores = await lenta_client.get_city_stores(nearest_city.id)
    stores = sorted(city_stores, key=lambda s: distance_between_points(latitude, longitude, s.lat, s.long))
    return stores[0]

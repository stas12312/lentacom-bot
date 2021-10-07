import datetime
import logging
from collections import defaultdict
from typing import Optional, NamedTuple

import asyncpg
from aiogram import Bot

from lenta.client import LentaClient
from lenta.models import BaseSku
from tgbot.services.messages import get_sku_info_message
from tgbot.services.repository import Repo


class UserInfo(NamedTuple):
    user_id: int
    store_id: str


async def get_discounts_for_skus(pool: asyncpg.Pool, lenta_client: LentaClient, bot: Bot) -> None:
    """Получение сегодняшних скидок по товарам в магазинах"""
    async with pool.acquire() as conn:
        repo = Repo(conn)
        now = datetime.datetime.now()
        sku_data = await _get_sku_data(repo, lenta_client)
        user_store_skus = await _get_user_store_skus_data(repo)

        user_discount_skus = _get_user_skus_with_discount(sku_data, user_store_skus)
        await send_messages(bot, user_discount_skus)


async def _get_sku_data(repo: Repo, lenta_client: LentaClient) -> dict[str, dict[str, Optional[BaseSku]]]:
    """Получение информации о продуктах"""
    store_skus = await repo.get_store_skus()

    # Собираем информацию о магазинах и продуктах в них
    store_sku_id_to_sku = _prepare_store_skus_data(store_skus)
    # Для каждого из магазинов получим связанный с ним список товаров
    # из API Lenta.com
    for store_id in store_sku_id_to_sku.keys():
        sku_ids = list(store_sku_id_to_sku[store_id].keys())
        sku_data = await lenta_client.get_store_skus_by_ids(store_id, sku_ids)
        for sku in sku_data:
            store_sku_id_to_sku[store_id][sku.code] = sku
    return store_sku_id_to_sku


def _prepare_store_skus_data(store_skus: list[asyncpg.Record]) -> dict[str, dict[str, Optional[BaseSku]]]:
    store_sku_id_to_sku: dict[str, dict[str, Optional[BaseSku]]] = defaultdict(dict)

    for item in store_skus:
        store_sku_id_to_sku[item.get("store_id")][item.get("sku_id")] = None
    return store_sku_id_to_sku


async def _get_user_store_skus_data(repo: Repo) -> dict[UserInfo, list]:
    """Преобразование данных о пользовательских магазинах и товаров"""
    user_store_skus = await repo.get_user_store_skus()
    return _prepare_user_store_skus_data(user_store_skus)


def _prepare_user_store_skus_data(user_store_skus: list[asyncpg.Record]) -> dict[UserInfo, list]:
    user_store_ids: dict[UserInfo, list] = defaultdict(list)
    for item in user_store_skus:
        user_store_id = UserInfo(item.get("user_id"), item.get("store_id"))
        user_store_ids[user_store_id].append(item.get("sku_id"))
    return user_store_ids


def _get_user_skus_with_discount(sku_data: dict[str, dict[str, Optional[BaseSku]]],
                                 user_store_skus: dict[UserInfo, list]) -> list[tuple[int, list[BaseSku]]]:
    user_skus: list[tuple[int, list[BaseSku]]] = []

    for user_store_id, sku_ids in user_store_skus.items():
        user_id, store_id = user_store_id.user_id, user_store_id.store_id

        sku_details = []
        for sku_id in sku_ids:
            sku = sku_data[store_id][sku_id]
            if sku.promo_type != "None":
                sku_details.append(sku)

        user_skus.append((user_id, sku_details))

    return user_skus


async def send_messages(bot: Bot, user_skus: list[tuple[int, list[BaseSku]]]) -> None:
    """Рассылка сообщений о скидках"""
    for user_id, skus in user_skus:
        try:
            message = "\n\n".join([
                "🎁 Скидки на сегодня" if skus else "😢 На ваши товары сегодня скидок нет",
                *[get_sku_info_message(sku) for sku in skus]
            ])
            await bot.send_message(user_id, message)
        except Exception as e:
            logging.error(e)

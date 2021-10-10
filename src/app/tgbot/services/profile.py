from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lenta.client import LentaClient
from lenta.models import Store, BaseSku
from tgbot.callbacks.profile import add_sku_cb
from tgbot.services.repository import Repo


async def get_store_for_user(lenta_client: LentaClient, repo: Repo, user_id: int) -> Optional[Store]:
    """
    Получение магазина пользователя
    """

    store_id = await get_user_store_id(repo, user_id)
    return await lenta_client.get_store(store_id) if store_id else None


async def get_user_store_id(repo: Repo, user_id: int) -> str:
    """Получение идентификатора магазина пользователя"""
    return await repo.get_user_store_id(user_id)


async def save_store_for_user(repo: Repo, user_id: int, store_id: str) -> None:
    """Сохранение магазина пользователя"""
    await repo.set_store_to_user(store_id, user_id)


def get_add_sku_keyboard(sku_id: str) -> InlineKeyboardMarkup:
    """Получение клавиатуры для добавление товара"""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Добавить товар", callback_data=add_sku_cb.new(sku_id))
    )


async def get_user_skus(user_id: int, repo: Repo, lenta_client: LentaClient) -> list[BaseSku]:
    """Получение информации о товарах пользователя"""
    sku_ids = await repo.get_user_sku_ids(user_id)
    store_id = await repo.get_user_store_id(user_id)
    return await lenta_client.get_store_skus_by_ids(store_id, sku_ids) if sku_ids else []


async def get_user_sku(user_id: int, sku_code: str, repo: Repo, lenta_client: LentaClient) -> BaseSku:
    store_id = await repo.get_user_store_id(user_id)
    return await lenta_client.get_sku(store_id, sku_code)


async def search_skus_in_user_store(user_id: int, sku_name: str,
                                    repo: Repo, lenta_client: LentaClient) -> list[BaseSku]:
    """Получение товаров по совпадению в названии"""
    store_id = await repo.get_user_store_id(user_id)
    return await lenta_client.search_skus_in_store(store_id, sku_name)

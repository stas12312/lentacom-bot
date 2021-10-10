from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lenta.client import LentaClient
from lenta.models import BaseSku, DetailCategory
from tgbot.callbacks.profile import choice_group, choice_category, choice_subcategory


async def search_sku_in_store(store_id: str, sku_name: str, lenta_client: LentaClient) -> list[BaseSku]:
    """Получение товаров по совпадению в названии"""
    return await lenta_client.search_skus_in_store(store_id, sku_name)


async def get_catalog_groups(lenta_client: LentaClient, store_id: str) -> list[DetailCategory]:
    """Получение корня каталога"""
    catalog = await lenta_client.get_catalog(store_id)
    return catalog.catalog_groups


async def get_group_categories(lenta_client: LentaClient, store_id: str,
                               group_category_code: str) -> list[DetailCategory]:
    """Получение категорий группы"""
    catalog = await lenta_client.get_catalog(store_id)
    for group in catalog.catalog_groups:
        if group.code == group_category_code:
            return group.categories
    return []


async def get_category_subcategories(lenta_client: LentaClient, store_id: str,
                                     category_code: str) -> list[DetailCategory]:
    """Получение подкатегорий категории"""

    # Пока сканируем все группы и категории
    catalog = await lenta_client.get_catalog(store_id)
    for group in catalog.catalog_groups:
        for category in group.categories:
            if category.code == category_code:
                return category.subcategories
    return []


async def get_category_skus(lenta_client: LentaClient, store_id: str, category_code: str) -> list[BaseSku]:
    """Получение товаров категории"""
    skus = await lenta_client.search_skus_in_store(store_id, node_code=category_code)
    return skus


def get_inline_keyboard_for_groups(groups: list[DetailCategory]) -> InlineKeyboardMarkup:
    """Получение клавиатура для выбора группы"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    for group in groups:
        cb_data = choice_group.new(group_code=group.code)
        keyboard.insert(
            InlineKeyboardButton(group.name, callback_data=cb_data)
        )
    return keyboard


def get_inline_keyboard_for_categories(categories: list[DetailCategory]) -> InlineKeyboardMarkup:
    """Получение клавиатуры для выбора категорий"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        cb_data = choice_category.new(category_code=category.code)
        keyboard.insert(
            InlineKeyboardButton(category.name, callback_data=cb_data)
        )
    return keyboard


def get_inline_keyboard_for_subcategories(subcategories: list[DetailCategory]) -> InlineKeyboardMarkup:
    """Получение клавиатуры для выбора подкатегорий"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    for subcategory in subcategories:
        cb_data = choice_subcategory.new(subcategory_code=subcategory.code)
        keyboard.insert(
            InlineKeyboardButton(subcategory.name, callback_data=cb_data)
        )
    return keyboard

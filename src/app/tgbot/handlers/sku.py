from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from lenta.client import LentaClient
from tgbot import services
from tgbot.callbacks.profile import choice_group, choice_category, choice_subcategory
from tgbot.keyboards import buttons
from tgbot.keyboards.menu import MAIN_MENU, CANCEL_MENU
from tgbot.keyboards.sku import get_sku_keyboard
from tgbot.models.states import SearchSku
from tgbot.services.repository import Repo


async def start_search_sku(msg: Message):
    """Начало процесса поиска товара"""
    await SearchSku.select_sku.set()
    await msg.answer("Введите название продукта", reply_markup=CANCEL_MENU)


async def show_founded_skus(msg: Message, repo: Repo, lenta: LentaClient, state: FSMContext):
    """Получение и отображение найденных продуктов"""
    sku_name = msg.text
    user_store_id = await services.profile.get_user_store_id(repo, msg.from_user.id)
    skus = await services.sku.search_sku_in_store(user_store_id, sku_name, lenta)
    skus_info_message = services.messages.get_sku_list_message("🗒 Найденные продукты", skus, True)
    await msg.answer(skus_info_message, reply_markup=MAIN_MENU)
    await state.finish()


async def show_sku_detail(msg: Message, repo: Repo, lenta: LentaClient):
    """Получение карточки продкута"""
    sku_code = msg.text.split("_")[1]
    sku = await services.profile.get_user_sku(msg.from_user.id, sku_code, repo, lenta)
    sku_info_message = services.messages.get_sku_info_message(sku)
    sku_keyboard = await get_sku_keyboard(msg.from_user.id, sku_code, repo)
    await msg.answer(sku_info_message, reply_markup=sku_keyboard)


async def show_category_groups(msg: Message, repo: Repo, lenta: LentaClient):
    """Отображение групп категорий"""
    user_store_id = await services.profile.get_user_store_id(repo, msg.from_user.id)
    groups = await services.sku.get_catalog_groups(lenta, user_store_id)
    keyboard = services.sku.get_inline_keyboard_for_groups(groups)
    await msg.answer("Выберите группу", reply_markup=keyboard)


async def show_categories(callback: CallbackQuery, repo: Repo, lenta: LentaClient, callback_data: dict[str, str]):
    """Отображение категорий товаров"""
    user_store_id = await services.profile.get_user_store_id(repo, callback.from_user.id)
    group_category_code = callback_data["group_code"]
    categories = await services.sku.get_group_categories(lenta, user_store_id, group_category_code)
    keyboard = services.sku.get_inline_keyboard_for_categories(categories)
    await callback.message.edit_text("Выберите категорию", reply_markup=keyboard)


async def show_subcategories(callback: CallbackQuery, repo: Repo, lenta: LentaClient, callback_data: dict[str, str]):
    """Отображение подкатегорий"""
    user_store_id = await services.profile.get_user_store_id(repo, callback.from_user.id)
    category_code = callback_data["category_code"]
    subcategories = await services.sku.get_category_subcategories(lenta, user_store_id, category_code)
    keyboard = services.sku.get_inline_keyboard_for_subcategories(subcategories)
    await callback.message.edit_text("Выберите подкатегорию", reply_markup=keyboard)


async def show_subcategory_skus(callback: CallbackQuery, repo: Repo, lenta: LentaClient, callback_data: dict[str, str]):
    """Отображение товаров подкатегории"""
    user_store_id = await services.profile.get_user_store_id(repo, callback.from_user.id)
    subcategory_code = callback_data["subcategory_code"]
    skus = await services.sku.get_category_skus(lenta, user_store_id, subcategory_code)
    if skus:
        msg = services.messages.get_sku_list_message("Товары категории", skus, True)
    else:
        msg = "Товары не найдены"
    await callback.message.edit_text(msg)


def register_sku(dp: Dispatcher) -> None:
    dp.register_message_handler(start_search_sku, text=buttons.SEARCH_SKU)
    dp.register_message_handler(show_founded_skus, state=SearchSku.select_sku)
    dp.register_message_handler(show_sku_detail, Text(startswith="/detail_"))
    dp.register_message_handler(show_category_groups, text=buttons.CATALOG)
    dp.register_callback_query_handler(show_categories, choice_group.filter())
    dp.register_callback_query_handler(show_subcategories, choice_category.filter())
    dp.register_callback_query_handler(show_subcategory_skus, choice_subcategory.filter())

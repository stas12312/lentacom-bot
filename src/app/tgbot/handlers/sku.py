from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from lenta.client import LentaClient
from tgbot import services
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


def register_sku(dp: Dispatcher) -> None:
    dp.register_message_handler(start_search_sku, text=buttons.SEARCH_SKU)
    dp.register_message_handler(show_founded_skus, state=SearchSku.select_sku)
    dp.register_message_handler(show_sku_detail, Text(startswith="/detail_"))

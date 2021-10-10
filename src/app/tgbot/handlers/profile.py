from io import BytesIO

from PIL import Image
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType
from pyzbar.pyzbar import decode

from lenta.client import LentaClient
from tgbot.callbacks.profile import add_sku_cb, delete_sku_cb
from tgbot.keyboards import buttons
from tgbot.keyboards.menu import MAIN_MENU, CANCEL_MENU
from tgbot.keyboards.sku import get_sku_keyboard
from tgbot.models.states import SearchSku
from tgbot import services
from tgbot.services.repository import Repo


async def add_sku(query: CallbackQuery, repo: Repo, callback_data: dict[str, str]):
    """Добавление товара пользователю"""
    sku_id = callback_data["sku_code"]
    await repo.add_sku_to_user(query.from_user.id, sku_id)
    await query.answer("Товар добавлен")
    sku_keyboard = await get_sku_keyboard(query.from_user.id, sku_id, repo)
    await query.message.edit_reply_markup(sku_keyboard)


async def delete_sku(query: CallbackQuery, repo: Repo, callback_data: dict[str, str]):
    """Удаление товара из списка пользователя"""
    sku_id = callback_data["sku_code"]
    await repo.delete_user_sku(query.from_user.id, sku_id)
    await query.answer("Товар удалён")
    sku_keyboard = await get_sku_keyboard(query.from_user.id, sku_id, repo)
    await query.message.edit_reply_markup(sku_keyboard)


async def show_user_store(msg: Message, repo: Repo, lenta: LentaClient):
    """
    Получение информации о магазине пользователя
    :param msg:
    :param repo:
    :param lenta:
    :return:
    """
    user_id = msg.from_user.id
    store = await services.profile.get_store_for_user(lenta, repo, user_id)
    if not store:
        await msg.answer("У вас не выбран магазин")
        return
    await msg.answer_location(latitude=store.lat, longitude=store.long)
    await msg.answer(services.messages.get_store_info_message(store))


async def show_sku_info_by_photo(msg: Message, lenta: LentaClient, repo: Repo):
    user_id = msg.from_user.id
    store = await services.profile.get_store_for_user(lenta, repo, user_id)
    blob = BytesIO()
    await msg.photo[-1].download(destination_file=blob)
    image = Image.open(blob)
    barcodes = decode(image)

    # Обрабатываем только первый barcode
    barcode = barcodes[0] if barcodes else None
    if barcode is None:
        await msg.answer("На изображении не найден штрих код")
        return

    store = await services.profile.get_store_for_user(lenta, repo, user_id)
    if store is None:
        await msg.answer("Требуется указать магазин")
        return

    sku = await lenta.get_sku_in_store_by_barcode(store.id, barcode.data.decode())
    if not sku:
        await msg.answer("Товар не найден")
        return

    sku_message_info = services.messages.get_sku_info_message(sku, barcode.data.decode())
    sku_keyboard = await get_sku_keyboard(msg.from_user.id, sku.code, repo)

    await msg.answer_photo(sku.image.medium, caption=sku_message_info, reply_markup=sku_keyboard)


async def show_user_skus(msg: Message, lenta: LentaClient, repo: Repo):
    """Получение товаров пользователя"""
    skus = await services.profile.get_user_skus(msg.from_user.id, repo, lenta)
    skus_info_message = services.messages.get_sku_list_message("🗒 Список добавленных товаров", skus, True)
    await msg.answer(skus_info_message)


async def start_search_sku(msg: Message):
    """Начало процесса поиска товара"""
    await SearchSku.select_sku.set()
    await msg.answer("Введите название продукта", reply_markup=CANCEL_MENU)


async def show_founded_skus(msg: Message, repo: Repo, lenta: LentaClient, state: FSMContext):
    """Получение и отображение найденных продуктов"""
    sku_name = msg.text
    skus = await services.profile.search_skus_in_user_store(msg.from_user.id, sku_name, repo, lenta)
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


def register_profile(dp: Dispatcher):
    dp.register_message_handler(show_user_store, text=buttons.MY_STORE)
    dp.register_message_handler(show_sku_info_by_photo, content_types=ContentType.PHOTO)
    dp.register_message_handler(show_user_skus, text=buttons.MY_SKUS)
    dp.register_message_handler(start_search_sku, text=buttons.SEARCH_SKU)
    dp.register_message_handler(show_founded_skus, state=SearchSku.select_sku)
    dp.register_message_handler(show_sku_detail, Text(startswith="/detail_"))

    dp.register_callback_query_handler(add_sku, add_sku_cb.filter(), state="*")
    dp.register_callback_query_handler(delete_sku, delete_sku_cb.filter(), state="*")

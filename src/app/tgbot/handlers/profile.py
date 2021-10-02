from io import BytesIO

import aiogram.utils.markdown as md
from PIL import Image
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup
from pyzbar.pyzbar import decode

from lenta.client import LentaClient
from tgbot.callbacks.profile import city_cb, store_cb, add_sku_cb
from tgbot.keyboards.buttons import ADD_STORE, MY_STORE, MY_SKUS
from tgbot.keyboards.menu import MAIN_MENU
from tgbot.models.states import AddStoreForm
from tgbot.services import messages
from tgbot.services.profile import (get_inline_keyboard_for_cities, get_inline_keyboard_for_city_stores,
                                    get_store_for_user, save_store_for_user, get_add_sku_keyboard,
                                    get_user_skus)
from tgbot.services.repository import Repo


async def start_select_city(msg: Message, lenta: LentaClient, repo: Repo):
    """
    Начало процесса выбора магазина
    Отображение доступных городов
    """
    city_keyboard = await get_inline_keyboard_for_cities(lenta)
    await msg.answer("Список доступных городов", reply_markup=city_keyboard)
    await AddStoreForm.city_id.set()


async def choice_city(query: CallbackQuery, repo: Repo, lenta: LentaClient,
                      state: FSMContext, callback_data: dict[str, str]):
    """
    Обработка выбора города
    """
    await query.answer()
    city_id = callback_data["city_id"]

    await state.update_data(city_id=city_id)

    await AddStoreForm.next()

    store_keyboard = await get_inline_keyboard_for_city_stores(lenta, city_id)
    await query.message.edit_text("Выберите магазин", reply_markup=store_keyboard)


async def add_sku(query: CallbackQuery, repo: Repo, callback_data: dict[str, str]):
    """Добавление товара пользователю"""
    sku_id = callback_data["sku_code"]
    await repo.add_sku_to_user(query.from_user.id, sku_id)
    await query.answer("Товар добавлен")
    await query.message.edit_reply_markup(InlineKeyboardMarkup())


async def choice_store(query: CallbackQuery, lenta: LentaClient, repo: Repo,
                       state: FSMContext, callback_data: dict[str, str]):
    """
    Обработка выбора магазина
    """
    user_id = query.from_user.id
    await query.answer()
    await query.message.delete()

    async with state.proxy() as data:
        data["store_id"] = callback_data["store_id"]
        await save_store_for_user(repo, user_id, data["store_id"])
        await query.message.answer(
            md.text("Магазин добавлен"),
            reply_markup=MAIN_MENU,
        )

    await state.finish()


async def show_user_store(msg: Message, repo: Repo, lenta: LentaClient):
    """
    Получение информации о магазине пользователя
    :param msg:
    :param repo:
    :param lenta:
    :return:
    """
    user_id = msg.from_user.id
    store = await get_store_for_user(lenta, repo, user_id)
    if not store:
        await msg.answer("У вас не выбран магазин")
        return

    await msg.answer(messages.get_store_info_message(store))


async def show_sku_info_by_photo(msg: Message, lenta: LentaClient, repo: Repo):
    user_id = msg.from_user.id
    store = await get_store_for_user(lenta, repo, user_id)
    blob = BytesIO()
    await msg.photo[-1].download(destination_file=blob)
    image = Image.open(blob)
    barcodes = decode(image)

    # Обрабатываем только первый barcode
    barcode = barcodes[0] if barcodes else None
    if barcode is None:
        await msg.answer("На изображении не найден штрих код")
        return

    store = await get_store_for_user(lenta, repo, user_id)
    if store is None:
        await msg.answer("Требуется указать магазин")
        return

    sku = await lenta.get_sku_in_store_by_barcode(store.id, barcode.data.decode())
    if not sku:
        await msg.answer("Товар не найден")
        return

    sku_message_info = messages.get_sku_info_message(sku, barcode.data.decode())
    await msg.answer_photo(sku.image.medium, caption=sku_message_info,
                           reply_markup=get_add_sku_keyboard(sku.code))


async def show_user_skus(msg: Message, lenta: LentaClient, repo: Repo):
    """Получение товаров пользователя"""
    skus = await get_user_skus(msg.from_user.id, repo, lenta)
    skus_info_message = messages.get_sku_list_message(skus)
    await msg.answer(skus_info_message)


def register_profile(db: Dispatcher):
    db.register_message_handler(start_select_city, text=ADD_STORE)
    db.register_message_handler(show_user_store, text=MY_STORE)
    db.register_message_handler(show_sku_info_by_photo, content_types=ContentType.PHOTO)
    db.register_message_handler(show_user_skus, text=MY_SKUS)
    db.register_callback_query_handler(choice_city, city_cb.filter(), state=AddStoreForm.city_id)
    db.register_callback_query_handler(choice_store, store_cb.filter(), state=AddStoreForm.store_id)
    db.register_callback_query_handler(add_sku, add_sku_cb.filter(), state="*")

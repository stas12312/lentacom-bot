import logging
from io import BytesIO

import aiogram.utils.markdown as md
from PIL import Image
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from pyzbar.pyzbar import decode

from lenta.client import LentaClient
from tgbot.callbacks.profile import city_cb, store_cb
from tgbot.keyboards.buttons import ADD_STORE, MY_STORE
from tgbot.keyboards.menu import MAIN_MENU
from tgbot.models.states import AddStoreForm
from tgbot.services.profile import (get_inline_keyboard_for_cities, get_inline_keyboard_for_city_stores,
                                    get_store_for_user, save_store_for_user)
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

    await msg.answer(
        md.text(f"Ваш магазин: {md.escape_md(store.name)} в {md.escape_md(store.city_name)}\n"
                f"Расположен по адресу: {md.escape_md(store.address)}\n"
                f"Время работы: {store.opens_at}\-{store.closes_at}")
    )


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

    price_postfix = "кг." if sku.is_weight_product else "шт."
    price = sku.discount_price if sku.discount_price else sku.regular_price
    discount = round(sku.regular_price - sku.discount_price, 2) if sku.discount_price else "Отсутствует"
    await msg.answer_photo(sku.image.medium,
                           caption=f"[{barcode.data.decode()}]\n"
                                   f"Товар найден : {md.escape_md(sku.title)}\n"
                                   f"Цена: {md.escape_md(price)} за {md.escape_md(price_postfix)}\n"
                                   f"Скидка: {md.escape_md(discount)}")


def register_profile(db: Dispatcher):
    db.register_message_handler(start_select_city, text=ADD_STORE)
    db.register_message_handler(show_user_store, text=MY_STORE)
    db.register_message_handler(show_sku_info_by_photo, content_types=ContentType.PHOTO)
    db.register_callback_query_handler(choice_city, city_cb.filter(), state=AddStoreForm.city_id)
    db.register_callback_query_handler(choice_store, store_cb.filter(), state=AddStoreForm.store_id)

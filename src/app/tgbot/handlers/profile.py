from io import BytesIO

import aiogram.utils.markdown as md
from PIL import Image
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType
from pyzbar.pyzbar import decode

from lenta.client import LentaClient
from tgbot.callbacks.profile import city_cb, store_cb, add_sku_cb, delete_sku_cb
from tgbot.keyboards import buttons
from tgbot.keyboards.menu import MAIN_MENU, CANCEL_MENU
from tgbot.keyboards.sku import get_sku_keyboard
from tgbot.models.states import AddStoreForm, SearchSku
from tgbot.services import messages, profile
from tgbot.services.repository import Repo


async def start_select_city(msg: Message, lenta: LentaClient, repo: Repo):
    """
    Начало процесса выбора магазина
    Отображение доступных городов
    """
    city_keyboard = await profile.get_inline_keyboard_for_cities(lenta)
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

    store_keyboard = await profile.get_inline_keyboard_for_city_stores(lenta, city_id)
    await query.message.edit_text("Выберите магазин", reply_markup=store_keyboard)


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
        await profile.save_store_for_user(repo, user_id, data["store_id"])
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
    store = await profile.get_store_for_user(lenta, repo, user_id)
    if not store:
        await msg.answer("У вас не выбран магазин")
        return
    await msg.answer_location(latitude=store.lat, longitude=store.long)
    await msg.answer(messages.get_store_info_message(store))


async def show_sku_info_by_photo(msg: Message, lenta: LentaClient, repo: Repo):
    user_id = msg.from_user.id
    store = await profile.get_store_for_user(lenta, repo, user_id)
    blob = BytesIO()
    await msg.photo[-1].download(destination_file=blob)
    image = Image.open(blob)
    barcodes = decode(image)

    # Обрабатываем только первый barcode
    barcode = barcodes[0] if barcodes else None
    if barcode is None:
        await msg.answer("На изображении не найден штрих код")
        return

    store = await profile.get_store_for_user(lenta, repo, user_id)
    if store is None:
        await msg.answer("Требуется указать магазин")
        return

    sku = await lenta.get_sku_in_store_by_barcode(store.id, barcode.data.decode())
    if not sku:
        await msg.answer("Товар не найден")
        return

    sku_message_info = messages.get_sku_info_message(sku, barcode.data.decode())
    sku_keyboard = await get_sku_keyboard(msg.from_user.id, sku.code, repo)

    await msg.answer_photo(sku.image.medium, caption=sku_message_info, reply_markup=sku_keyboard)


async def show_user_skus(msg: Message, lenta: LentaClient, repo: Repo):
    """Получение товаров пользователя"""
    skus = await profile.get_user_skus(msg.from_user.id, repo, lenta)
    skus_info_message = messages.get_sku_list_message("🗒 Список добавленных товаров", skus, True)
    await msg.answer(skus_info_message)


async def start_search_sku(msg: Message):
    """Начало процесса поиска товара"""
    await SearchSku.select_sku.set()
    await msg.answer("Введите название продукта", reply_markup=CANCEL_MENU)


async def show_founded_skus(msg: Message, repo: Repo, lenta: LentaClient, state: FSMContext):
    """Получение и отображение найденных продуктов"""
    sku_name = msg.text
    skus = await profile.search_skus_in_user_store(msg.from_user.id, sku_name, repo, lenta)
    skus_info_message = messages.get_sku_list_message("🗒 Найденные продукты", skus, True)
    await msg.answer(skus_info_message, reply_markup=MAIN_MENU)
    await state.finish()


async def show_sku_detail(msg: Message, repo: Repo, lenta: LentaClient):
    """Получение карточки продкута"""
    sku_code = msg.text.split("_")[1]
    sku = await profile.get_user_sku(msg.from_user.id, sku_code, repo, lenta)
    sku_info_message = messages.get_sku_info_message(sku)
    sku_keyboard = await get_sku_keyboard(msg.from_user.id, sku_code, repo)
    await msg.answer(sku_info_message, reply_markup=sku_keyboard)


def register_profile(db: Dispatcher):
    db.register_message_handler(start_select_city, text=buttons.ADD_STORE)
    db.register_message_handler(show_user_store, text=buttons.MY_STORE)
    db.register_message_handler(show_sku_info_by_photo, content_types=ContentType.PHOTO)
    db.register_message_handler(show_user_skus, text=buttons.MY_SKUS)
    db.register_message_handler(start_search_sku, text=buttons.SEARCH_SKU)
    db.register_message_handler(show_founded_skus, state=SearchSku.select_sku)
    db.register_message_handler(show_sku_detail, Text(startswith="/detail_"))
    db.register_callback_query_handler(choice_city, city_cb.filter(), state=AddStoreForm.city_id)
    db.register_callback_query_handler(choice_store, store_cb.filter(), state=AddStoreForm.store_id)
    db.register_callback_query_handler(add_sku, add_sku_cb.filter(), state="*")
    db.register_callback_query_handler(delete_sku, delete_sku_cb.filter(), state="*")

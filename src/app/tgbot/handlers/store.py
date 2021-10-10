import aiogram.utils.markdown as md
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from lenta.client import LentaClient
from tgbot import services
from tgbot.callbacks.profile import city_cb, store_cb
from tgbot.keyboards import buttons
from tgbot.keyboards.menu import MAIN_MENU, SEND_LOCATION
from tgbot.models.states import AddStoreForm
from tgbot.services.repository import Repo


async def start_select_city(msg: Message, lenta: LentaClient, repo: Repo, state: FSMContext):
    """
    Начало процесса выбора магазина
    Отображение доступных городов
    """
    city_keyboard = await services.store.get_inline_keyboard_for_cities(lenta)
    await AddStoreForm.select_city.set()

    # Сохраняем ID сообщения в хранилище для возможности его удаления вне inline клавиатуры
    await msg.answer("Выбор магазина", reply_markup=SEND_LOCATION)
    choice_city_msg = await msg.answer("Список доступных городов", reply_markup=city_keyboard)
    await state.update_data(message_id=choice_city_msg.message_id)


async def choice_store_by_location(msg: Message, repo: Repo, lenta: LentaClient, state: FSMContext):
    data = await state.get_data()
    await msg.bot.delete_message(msg.from_user.id, data["message_id"])
    await state.finish()

    store = await services.store.get_store_by_coodrinites(lenta, msg.location.latitude, msg.location.longitude)
    await services.profile.save_store_for_user(repo, msg.from_user.id, store.id)
    await msg.answer_location(latitude=store.lat, longitude=store.long)
    await msg.answer(
        f"Выбран ближайший магазин:\n"
        f"{services.messages.get_store_info_message(store)}",
        reply_markup=MAIN_MENU,
    )


async def choice_city(query: CallbackQuery, repo: Repo, lenta: LentaClient,
                      state: FSMContext, callback_data: dict[str, str]):
    """
    Обработка выбора города
    """
    await query.answer()
    city_id = callback_data["city_id"]

    await state.update_data(city_id=city_id)

    await AddStoreForm.next()

    store_keyboard = await services.store.get_inline_keyboard_for_city_stores(lenta, city_id)
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
        await services.profile.save_store_for_user(repo, user_id, data["store_id"])
        await query.message.answer(
            md.text("Магазин выбран"),
            reply_markup=MAIN_MENU,
        )

    await state.finish()


def register_store(dp: Dispatcher) -> None:
    dp.register_message_handler(start_select_city, text=buttons.ADD_STORE)

    dp.register_message_handler(choice_store_by_location, content_types=ContentType.LOCATION,
                                state=[AddStoreForm.select_city, AddStoreForm.select_store])
    dp.register_callback_query_handler(choice_city, city_cb.filter(), state=AddStoreForm.select_city)
    dp.register_callback_query_handler(choice_store, store_cb.filter(), state=AddStoreForm.select_store)

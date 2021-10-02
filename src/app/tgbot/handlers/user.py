from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.keyboards import buttons
from tgbot.keyboards.menu import MAIN_MENU
from tgbot.services.repository import Repo


async def user_start(m: Message, repo: Repo):
    await repo.add_user(m.from_user.id)
    await m.reply("Добро пожаловать 1", reply_markup=MAIN_MENU)


async def cancel(msg: Message, state: FSMContext):
    """Отмена действий"""
    await state.finish()
    await msg.answer("Действие отменено", reply_markup=MAIN_MENU)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(cancel, text=buttons.CANCEL, state="*")

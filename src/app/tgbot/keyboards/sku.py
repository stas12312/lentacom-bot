from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.repository import Repo
from ..callbacks.profile import add_sku_cb, delete_sku_cb


async def get_sku_keyboard(user_id: int, sku_code: str, repo: Repo) -> InlineKeyboardMarkup:
    """Получение клавиатуры карточки товара"""
    buttons: list[InlineKeyboardButton] = []
    if sku_code in await repo.get_user_sku_ids(user_id):
        buttons.append(InlineKeyboardButton("❌ Удалить товар из списка",
                                            callback_data=delete_sku_cb.new(sku_code=sku_code)))
    else:
        buttons.append(InlineKeyboardButton("⏬ Добавить товар в список",
                                            callback_data=add_sku_cb.new(sku_code=sku_code)))

    return InlineKeyboardMarkup(row_width=1).add(*buttons)

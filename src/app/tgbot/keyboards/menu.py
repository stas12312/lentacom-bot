from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.keyboards import buttons

MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.MY_SKUS), KeyboardButton(buttons.MY_STORE)],
    [KeyboardButton(buttons.ADD_STORE)],
    [KeyboardButton(buttons.SEARCH_SKU)],
], resize_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.CANCEL)],
], resize_keyboard=True)

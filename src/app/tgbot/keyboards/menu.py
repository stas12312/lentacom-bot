from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.keyboards import buttons

MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.MY_SKUS), KeyboardButton(buttons.MY_STORE)],
    [KeyboardButton(buttons.ADD_STORE)]
], resize_keyboard=True, one_time_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.CANCEL)]
], resize_keyboard=True)

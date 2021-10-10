from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.keyboards import buttons

MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.MY_SKUS), KeyboardButton(buttons.MY_STORE)],
    [KeyboardButton(buttons.ADD_STORE)],
    [KeyboardButton(buttons.SEARCH_SKU), KeyboardButton(buttons.CATALOG)],
], resize_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.CANCEL)],
], resize_keyboard=True)

SEND_LOCATION = ReplyKeyboardMarkup([
    [KeyboardButton(buttons.SEND_LOCATION, request_location=True)]
], resize_keyboard=True)

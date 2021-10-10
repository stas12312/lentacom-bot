from aiogram.dispatcher.filters.state import State, StatesGroup


class AddStoreForm(StatesGroup):
    select_city = State()
    select_store = State()


class SearchSku(StatesGroup):
    select_sku = State()

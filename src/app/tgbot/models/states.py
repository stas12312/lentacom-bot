from aiogram.dispatcher.filters.state import State, StatesGroup


class AddStoreForm(StatesGroup):
    city_id = State()
    store_id = State()

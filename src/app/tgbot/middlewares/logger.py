from datetime import datetime

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from analytics.client import AnaliyticsClient


class LoggerMiddleware(BaseMiddleware):
    skip_patterns = ["error"]

    def __init__(self, analytics_client: AnaliyticsClient):
        super().__init__()
        self._client = analytics_client

    @classmethod
    def _get_update_info(cls, update: types.Update) -> tuple[str, str]:
        """
        Получение действия пользователя
        :return:
        """

        if update.message:
            return update.message.content_type, update.message.text
        if update.callback_query:
            return "callback", cls._get_text_from_callback(update.callback_query)

    @classmethod
    def _get_text_from_callback(cls, callback: types.CallbackQuery) -> str:
        """Получение текста выбранной кнопки"""
        data = callback.data
        for rows in callback.message.reply_markup.inline_keyboard:
            for button in rows:
                if button.callback_data == data:
                    return button.text

    @classmethod
    def _get_message_from_update(cls, update: types.Update) -> types.Message:
        if update.callback_query:
            return update.callback_query.message
        if update.message:
            return update.message
        elif update.edited_message:
            return update.edited_message

    # noinspection PyMethodMayBeStatic
    async def on_pre_process_update(self, update: types.Update, data, *args) -> None:
        if not update.message and not update.callback_query:
            return

        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

        update_type, update_value = self._get_update_info(update)
        message = self._get_message_from_update(update)
        message_data = message.date if message else datetime.utcnow()

        await self._client.log(
            update_type, update_value,
            message_data,
            update.to_python(),
            user_id
        )

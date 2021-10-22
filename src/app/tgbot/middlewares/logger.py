import logging

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class LoggerMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        logging.info(obj)

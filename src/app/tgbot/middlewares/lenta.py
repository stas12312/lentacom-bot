from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from lenta.client import LentaClient


class LentaMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, lenta_client: LentaClient):
        super().__init__()
        self.lenta_client = lenta_client

    async def pre_process(self, obj, data, *args):
        data["lenta"] = self.lenta_client

    async def post_process(self, obj, data, *args):
        del data["lenta"]

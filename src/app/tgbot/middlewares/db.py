import asyncpg
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tgbot.services.repository import Repo


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, pool: asyncpg.Pool):
        super().__init__()
        self.pool = pool

    async def pre_process(self, obj, data, *args):
        db = await self.pool.acquire()
        data["dp"] = db
        data["repo"] = Repo(db)

    async def post_process(self, obj, data, *args):
        del data["repo"]
        db = data.get("dp")
        if db:
            await db.close()

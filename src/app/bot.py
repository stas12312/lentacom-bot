import asyncio
import logging

import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.types import BotCommand, ParseMode

from lenta.client import LentaClient
from tgbot.config import load_config, COMMANDS
from tgbot.handlers.profile import register_profile
from tgbot.handlers.user import register_user
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.lenta import LentaMiddleware
from tgbot.services.db import create_db

logger = logging.getLogger(__name__)


def create_pool(connection_string: str, echo: bool) -> asyncpg.Pool:
    return asyncpg.create_pool(connection_string)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config = load_config()

    if config.TG_USE_REDIS:
        storage = RedisStorage(host=config.REDIS_HOST)
    else:
        storage = MemoryStorage()
    pool: asyncpg.Pool = await create_pool(
        config.PG_CONNECTION_STRING,
        echo=False,
    )

    bot = Bot(token=config.TG_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(LentaMiddleware(LentaClient()))
    register_profile(dp)
    register_user(dp)

    async with pool.acquire() as conn:
        await create_db(conn)

    await bot.set_my_commands([BotCommand(*cmd) for cmd in COMMANDS])
    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

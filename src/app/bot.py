import asyncio
import datetime
import logging

import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.types import BotCommand, ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from analytics.client import AnaliyticsClient
from lenta.cache.memory import MemoryCache
from lenta.cache.redis import RedisCache
from lenta.client import LentaClient
from tgbot.config import load_config, COMMANDS
from tgbot.handlers.profile import register_profile
from tgbot.handlers.sku import register_sku
from tgbot.handlers.store import register_store
from tgbot.handlers.user import register_user
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.lenta import LentaMiddleware
from tgbot.middlewares.logger import LoggerMiddleware
from tgbot.services.lenta import get_discounts_for_skus

logger = logging.getLogger(__name__)


def create_pool(connection_string: str, echo: bool) -> asyncpg.Pool:
    return asyncpg.create_pool(connection_string)


def register_handlers(dp: Dispatcher) -> None:
    register_user(dp)
    register_profile(dp)
    register_store(dp)
    register_sku(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    config = load_config()

    if config.TG_USE_REDIS:
        storage = RedisStorage(host=config.REDIS_HOST)
        cache = RedisCache(host=config.REDIS_HOST)
    else:
        storage = MemoryStorage()
        cache = MemoryCache()

    pool: asyncpg.Pool = await create_pool(
        config.PG_CONNECTION_STRING,
        echo=False,
    )

    bot = Bot(token=config.TG_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    dp = Dispatcher(bot, storage=storage)
    analitycs = AnaliyticsClient(
        config.INFLUXDB_HOST,
        config.INFLUXDB_USER,
        config.INFLUXDB_USER_PASSWORD,
        config.INFLUXDB_DB,
    )
    lenta_client = LentaClient(cache_storage=cache)
    scheduler = AsyncIOScheduler()

    register_handlers(dp)

    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(LentaMiddleware(lenta_client))
    dp.middleware.setup(LoggerMiddleware(analitycs))

    await bot.set_my_commands([BotCommand(*cmd) for cmd in COMMANDS])
    # start
    try:
        logging.info(datetime.datetime.now())
        scheduler.start()
        scheduler.add_job(get_discounts_for_skus, "cron", minute=0, hour=0, second=0, args=(pool, lenta_client, bot))
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await cache.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

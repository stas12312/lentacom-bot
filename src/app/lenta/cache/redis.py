import asyncio
import json
import typing

import aioredis

from .base import BaseCache


class RedisCache(BaseCache):

    def __init__(self,
                 host: str = "localhost",
                 port: int = 6379,
                 db: typing.Optional[int] = None,
                 password: typing.Optional[str] = None,
                 ssl: typing.Optional[bool] = None,
                 pool_size: int = 10,
                 prefix_key: str = "lenta_cache",
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 **kwargs
                 ):
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._ssl = ssl
        self._pool_size = pool_size
        self._prefix_key = prefix_key
        self._loop = loop or asyncio.get_event_loop()
        self._connection_lock = asyncio.Lock(loop=self._loop)
        self._redis: typing.Optional[aioredis.Redis] = None
        self._kwargs = kwargs

    async def _get_redis(self) -> aioredis.Redis:
        """Получение клиента для работы с Redis"""
        async with self._connection_lock:
            if self._redis is None:
                redis_version = int(aioredis.__version__.split(".")[0])
                if redis_version != 2:
                    raise RuntimeError(f"Unsupported aioredis version: {redis_version}")
                self._redis = aioredis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    password=self._password,
                    ssl=self._ssl,
                    max_connections=self._pool_size,
                    decode_responses=True,
                    **self._kwargs,
                )
        return self._redis

    async def get(self, key: str) -> typing.Optional[typing.Union[list, dict]]:
        redis = await self._get_redis()
        raw_value = await redis.get(key)
        return json.loads(raw_value)

    async def set(self, key: str, value: typing.Union[dict, list], ttl: int) -> None:
        redis = await self._get_redis()
        json_value = json.dumps(value)
        await redis.set(key, json_value, ttl)

    async def reset_all(self) -> None:
        if self._redis:
            await self._redis.flushdb()

    async def close(self):
        if self._redis:
            return await self._redis.close()

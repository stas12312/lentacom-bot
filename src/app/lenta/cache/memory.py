import time
import typing

from .base import BaseCache


class MemoryCache(BaseCache):

    def __init__(self):
        self._data = {}  # Словарь для хранения значений
        self._expired_info = {}  # Словарь для хранения информации об истечении жизни значения в кэше

    async def set(self, key: str, value: typing.Union[dict, list], ttl: int) -> None:
        self._data[key] = value
        self._expired_info[key] = time.time() + ttl

    async def get(self, key: str) -> typing.Optional[typing.Union[list, dict]]:
        if self._is_key_exists(key) and self._is_key_relevant(key):
            return self._data[key]
        return None

    def _is_key_exists(self, key: str) -> bool:
        """
        Проверка существования ключа
        :param key: Ключ
        :return:
        """
        # Проверка, что ключ есть в словаре
        return key in self._data

    def _is_key_relevant(self, key: str) -> bool:
        """
        Проверка актуальности ключа в кэше
        :param key: Ключ
        :return: Результат проверки
        """
        expired_time = self._expired_info.get(key)
        if expired_time is None:
            return False
        if expired_time < time.time():
            self._delete_key(key)
            return False

        return True

    def _delete_key(self, key) -> None:
        """Удаление ключа из кэша"""
        self._data.pop(key, None)
        self._expired_info.pop(key, None)

    async def reset_all(self) -> None:
        self._data = {}
        self._expired_info = {}

    async def close(self) -> None:
        await self.reset_all()

import logging
import time
from abc import ABC, abstractmethod
from typing import Union, Optional


class BaseCache(ABC):
    """Базоывй класс для кэширования запросов к Ленте"""

    @abstractmethod
    def set(self, key: str, value: str, ttl: int) -> None:
        """
        Сохранение значения по ключу в кэш
        :param key: Ключ
        :param value: Значение
        :param ttl: Время жизни записи в кэше в секундах
        :return:
        """

    @abstractmethod
    def get(self, key: str) -> Optional[Union[list, dict]]:
        """
        Получение значения из кэша
        :param key: Ключ
        :return: Значение по ключу
        """

    @abstractmethod
    def reset_all(self) -> None:
        """
        Очистка всего кэша
        :return:
        """


class MemoryCache(BaseCache):

    def __init__(self):
        self._data = {}  # Словарь для хранения значений
        self._expired_info = {}  # Словарь для хранения информации об истечении жизни значения в кэше

    def set(self, key: str, value: Union[list, dict], ttl: int) -> None:
        self._data[key] = value
        self._expired_info[key] = time.time() + ttl
        logging.info(f"{self._expired_info=}")

    def get(self, key: str) -> Optional[Union[list, dict]]:
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

    def reset_all(self) -> None:
        self._data = {}
        self._expired_info = {}


def create_key_by_args(*args, **kwargs) -> str:
    """
    Формирование ключа по списку параметров
    :param args: Список параметров
    :param kwargs: Словарь параметров
    :return: Ключ для кэширования
    """
    dict_args = [f"{key}:{value}" for key, value in kwargs.items()]
    key = "_".join([*args, *dict_args])
    return key

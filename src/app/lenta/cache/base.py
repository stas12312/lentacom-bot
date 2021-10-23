import typing
from abc import ABC, abstractmethod


class BaseCache(ABC):
    """Базоывй класс для кэширования запросов к Ленте"""

    @abstractmethod
    async def set(self, key: str, value: typing.Union[dict, list], ttl: int) -> None:
        """
        Сохранение значения по ключу в кэш
        :param key: Ключ
        :param value: Значение
        :param ttl: Время жизни записи в кэше в секундах
        :return:
        """

    @abstractmethod
    async def get(self, key: str) -> typing.Optional[typing.Union[list, dict]]:
        """
        Получение значения из кэша
        :param key: Ключ
        :return: Значение по ключу
        """

    @abstractmethod
    async def reset_all(self) -> None:
        """
        Очистка всего кэша
        :return:
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Закрытие соединения с кэшем
        :return:
        """


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

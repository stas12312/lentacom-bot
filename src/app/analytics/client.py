import json
from datetime import datetime

from aioinflux import InfluxDBClient, InfluxDBWriteError

from analytics.objects import BotUpdate


class AnaliyticsClient:

    def __init__(self, influx_host: str, influx_user: str, influx_password: str, influx_db: str):
        """Инициализация клиента для работы с InfluxDB"""
        self.client = InfluxDBClient(
            host=influx_host,
            username=influx_user,
            password=influx_password,
            database=influx_db,
        )

    async def log(self, update_type: str, value: str, event_datetime: datetime, update: dict, user_id: int):
        """
        Сохранение записи в InfluxDB

        :param update_type: Тип update
        :param value: Тип события
        :param event_datetime: Время события
        :param update: Объект update
        :return:
        """

        update = BotUpdate(
            measurement="updates",
            value=value,
            timestamp=event_datetime,
            update_type=update_type,
            update=json.dumps(update),
            stub=1,
            user_id=str(user_id),
        )

        try:
            await self.client.write(update)
        except InfluxDBWriteError as ex:
            print(ex)

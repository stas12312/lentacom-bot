import logging
from typing import Optional

import asyncpg


class Repo:

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def add_user(self, user_id: int, first_name: str, last_name: str) -> None:
        """Сохранение пользователя"""
        await self.conn.execute(
            "INSERT INTO users (id, first_name, last_name) VALUES ($1, $2, $3) ON CONFLICT (id) "
            "DO UPDATE SET first_name = $2, last_name = $3",
            user_id, first_name, last_name
        )
        return

    async def set_store_to_user(self, store_id: str, user_id: int):
        """Добавление магазина пользователю"""
        await self.conn.execute(
            "DELETE FROM user_store WHERE user_id=$1",
            user_id
        )
        await self.conn.execute(
            "INSERT INTO user_store (user_id, store_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, store_id
        )

    async def get_user_store_id(self, user_id: int) -> Optional[str]:
        """Получение магазинов пользователя"""
        row = await self.conn.fetchrow(
            "SELECT user_id, store_id FROM user_store WHERE user_id=$1",
            user_id
        )
        return None if not row else row["store_id"]

    async def add_sku_to_user(self, user_id: int, sku_id: str) -> None:
        """
        Добавление товара к пользователю
        """
        await self.conn.execute("INSERT INTO user_skus (user_id, sku_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                                user_id, sku_id)

    async def delete_user_sku(self, user_id: int, sku_id: str) -> None:
        """Удаление товара пользователя"""
        await self.conn.execute("DELETE FROM user_skus WHERE user_id = $1 AND sku_id = $2",
                                user_id, sku_id)

    async def get_user_sku_ids(self, user_id: int) -> list[str]:
        """Получение идентификаторов товаров"""
        rows = await self.conn.fetch(
            "SELECT sku_id FROM user_skus WHERE user_id=$1",
            user_id
        )

        return [row["sku_id"] for row in rows]

    async def get_store_skus(self) -> list[asyncpg.Record]:
        """Получение информации о всех товарах в бд"""
        rows = await self.conn.fetch(
            "SELECT DISTINCT st.store_id AS store_id, sk.sku_id AS sku_id"
            " FROM users AS u "
            "JOIN user_store AS st on u.id = st.user_id "
            "JOIN user_skus AS sk on u.id = sk.user_id "
        )
        logging.info(rows)
        return rows

    async def get_user_store_skus(self) -> list[asyncpg.Record]:
        """Получение информации о магазине и товарах пользователей"""
        rows = await self.conn.fetch(
            "SELECT u.id AS user_id, st.store_id AS store_id, sk.sku_id AS sku_id "
            "FROM users AS u "
            "JOIN user_store AS st on u.id = st.user_id "
            "JOIN user_skus AS sk on u.id = sk.user_id"
        )

        return rows

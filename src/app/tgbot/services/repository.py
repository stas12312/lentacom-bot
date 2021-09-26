from typing import Optional


class Repo:

    def __init__(self, conn):
        self.conn = conn

    async def add_user(self, user_id) -> None:
        """Сохранение пользователя"""
        await self.conn.execute(
            "INSERT INTO users (id) VALUES ($1) ON CONFLICT DO NOTHING",
            user_id,
        )
        return

    async def set_store_to_user(self, store_id: int, user_id: int):
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

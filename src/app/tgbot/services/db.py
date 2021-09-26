CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY
)
"""

CREATE_USER_STORE_SQL = """CREATE TABLE IF NOT EXISTS user_store (
    user_id BIGSERIAL REFERENCES users(id),
    store_id VARCHAR(10)
)"""

CREATE_USER_SKUS_SQL = """CREATE TABLE IF NOT EXISTS user_skus (
    user_id BIGSERIAL REFERENCES users(id),
    sku_id VARCHAR(10)
)"""

CREATE_STORE_USER_ID_IDX = """CREATE INDEX IF NOT EXISTS user_store_store_id_idx ON user_store (store_id)"""
CREATE_SKUS_USER_ID_IDX = """CREATE INDEX IF NOT EXISTS user_skus_sku_id_idx ON user_skus (sku_id)"""


async def create_db(conn):
    """
    Создание БД
    :param conn:
    :return:
    """
    await conn.execute(CREATE_USERS_SQL)
    await conn.execute(CREATE_USER_SKUS_SQL)
    await conn.execute(CREATE_USER_STORE_SQL)
    await conn.execute(CREATE_SKUS_USER_ID_IDX)
    await conn.execute(CREATE_STORE_USER_ID_IDX)

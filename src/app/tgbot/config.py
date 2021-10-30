from typing import Optional, Any, Dict

from pydantic import BaseSettings, PostgresDsn, validator

COMMANDS = [
    ("/start", "Регистрация заново")
]


class Config(BaseSettings):
    TG_TOKEN: str
    TG_ADMIN_ID: int
    TG_USE_REDIS: bool = False
    PG_HOST: str
    PG_PASSWORD: str
    PG_USER: str
    PG_DB: str
    REDIS_HOST: str
    INFLUXDB_HOST: str
    INFLUXDB_DB: str
    INFLUXDB_USER: str
    INFLUXDB_USER_PASSWORD: str
    PG_CONNECTION_STRING: Optional[PostgresDsn] = None

    @validator("PG_CONNECTION_STRING", pre=True)
    def build_db_connection_string(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("PG_USER"),
            password=values.get("PG_PASSWORD"),
            host=values.get("PG_HOST"),
            path=f"/{values.get('PG_DB') or ''}",
        )


def load_config() -> Config:
    """Загрузка конфигурации из переменных окружения"""
    return Config()

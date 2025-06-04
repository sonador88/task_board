import logging
from dataclasses import dataclass
from environs import Env
# import os


logger = logging.getLogger(__name__)


@dataclass
class BotConf:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class DatabaseConf:
    name: str       # Название базы данных
    host: str       # URL-адрес базы данных
    port: int       # порт базы данных
    username: str       # Username пользователя базы данных
    password: str   # Пароль к базе данных


@dataclass
class RedisConf:
    db: int
    host: str
    port: int
    username: str
    password: str


@dataclass
class LoggConf:
    level: str
    format: str


@dataclass
class Config:
    bot: BotConf
    db: DatabaseConf
    redis: RedisConf
    log: LoggConf


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    token = env("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN must not be empty")
    raw_ids = env.list("ADMIN_IDS", default=[])
    try:
        admin_ids = [int(x) for x in raw_ids]
    except ValueError as e:
        raise ValueError(f"ADMIN_IDS must be integers, got: {raw_ids}") from e
    bot = BotConf(token=token, admin_ids=admin_ids)

    db = DatabaseConf(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env("POSTGRES_PORT"),
        username=env("POSTGRES_USERNAME"),
        password=env("POSTGRES_PASSWORD"),
    )

    redis = RedisConf(
        db=env("REDIS_DB"),
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        username=env("REDIS_USERNAME"),
        password=env("REDIS_PASSWORD"),
    )

    logg_settings = LoggConf(
        level=env("LOG_LEVEL", default="DEBUG"),
        format=env("LOG_FORMAT")
    )

    logger.info("Configuration loaded successfully")

    return Config(
        bot=bot,
        db=db,
        redis=redis,
        log=logg_settings
    )
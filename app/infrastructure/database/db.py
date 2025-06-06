import logging
from datetime import datetime, timezone
# from app.bot.enums.roles import UserRole
from psycopg import AsyncConnection
from typing import Any


logger = logging.getLogger(__name__)


async def add_user(
    conn: AsyncConnection,
    *,
    user_id: int,
    firstname: str,
    lastname: str,
    username: str | None = None,
    language: str = "ru",
) -> None:
    '''
    Функция для добавления пользователя в систему
    '''
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO users(user_id, username, firstname, lastname, language)
                VALUES(
                    %(user_id)s,
                    %(username)s,
                    %(firstname)s,
                    %(lastname)s,
                    %(language)s
                ) ON CONFLICT DO NOTHING;
            """,
            params={
                "user_id": user_id,
                "username": username,
                "firstname": firstname,
                "lastname": lastname,
                "language": language
            },
        )
    logger.info(
        "User added. Table=`%s`, user_id=%d, created_at='%s', "
        "language='%s'",
        "users",
        user_id,
        datetime.now(timezone.utc),
        language,
    )


async def get_user(
    conn: AsyncConnection,
    *,
    user_id: int,
) -> tuple[Any, ...] | None:
    '''
    Функция для получения информации о пользователе по его user_id
    '''
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT
                    id,
                    user_id,
                    username,
                    firstname,
                    lastname,
                    language,
                    is_alive,
                    banned,
                    created_at
                    FROM users WHERE user_id = %s;
            """,
            params=(user_id,),
        )
        row = await data.fetchone()
    logger.info("Row is %s", row)
    return row if row else None


async def change_user_alive_status(
    conn: AsyncConnection,
    *,
    is_alive: bool,
    user_id: int,
) -> None:
    '''
    Функция для смены статуса активности юзера user_id
    '''
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET is_alive = %s
                WHERE user_id = %s;
            """,
            params=(is_alive, user_id)
        )
    logger.info("Updated `is_alive` status to `%s` for user %d", is_alive, user_id)


async def change_user_banned_status_by_id(
    conn: AsyncConnection,
    *,
    banned: bool,
    user_id: int,
) -> None:
    '''
    Функция для смены статуса юзера user_id (забанен или нет)
    '''
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET banned = %s
                WHERE user_id = %s
            """,
            params=(banned, user_id)
        )
    logger.info("Updated `banned` status to `%s` for user %d", banned, user_id)


async def update_user_lang(
    conn: AsyncConnection,
    *,
    language: str,
    user_id: int,
) -> None:
    '''
        Функция для изменения языка для пользователя user_id
    '''
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET language = %s
                WHERE user_id = %s
            """,
            params=(language, user_id)
        )
    logger.info("The language `%s` is set for the user `%s`",
                language, user_id)


async def get_user_lang(
    conn: AsyncConnection,
    *,
    user_id: int,
) -> str | None:
    '''
    Функция для получения языка пользователя
    '''
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT language FROM users WHERE user_id = %s;
            """,
            params=(user_id,),
        )
        row = await data.fetchone()
    if row:
        logger.info("The user with `user_id`=%s has the language %s", user_id, row[0])
    else:
        logger.warning(
            "No user with `user_id`=%s found in the database",
            user_id
            )
    return row[0] if row else None


async def get_user_alive_status(
    conn: AsyncConnection,
    *,
    user_id: int,
) -> bool | None:
    '''
    Функция для получения статуса пользователя
    '''
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT is_alive FROM users WHERE user_id = %s;
            """,
            params=(user_id,),
        )
        row = await data.fetchone()
    if row:
        logger.info("The user with `user_id`=%s has the is_alive status is %s", user_id, row[0])
    else:
        logger.warning("No user with `user_id`=%s found in the database", user_id)
    return row[0] if row else None


async def get_user_banned_status_by_id(
    conn: AsyncConnection,
    *,
    user_id: int,
) -> bool | None:
    '''
    Функция для получения статуса пользователя (забанен или нет)
    '''
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT banned FROM users WHERE user_id = %s;
            """,
            params=(user_id,),
        )
        row = await data.fetchone()
    if row:
        logger.info("The user with `user_id`=%s has the banned status is %s", user_id, row[0])
    else:
        logger.warning("No user with `user_id`=%s found in the database", user_id)
    return row[0] if row else None

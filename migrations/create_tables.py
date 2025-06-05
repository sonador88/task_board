import asyncio
import logging
import os
import sys

from app.infrastructure.database.connection import get_pg_connection
from config.config import Config, load_config
from psycopg import AsyncConnection, Error

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)
logger = logging.getLogger(__name__)


async def main():
    connection: AsyncConnection | None = None

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.username,
            password=config.db.password,
        )
        async with connection:
            async with connection.transaction():
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS users(
                                id SERIAL PRIMARY KEY,
                                user_id BIGINT NOT NULL UNIQUE COMMENT 'id пользователя в телеграмме',
                                username VARCHAR(50) COMMENT 'ник пользователя в телеграмме',
                                firstname VARCHAR(50) NOT NULL COMMENT 'имя пользователя',
                                lastname VARCHAR(50) NOT NULL COMMENT 'фамилия пользователя',
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                language VARCHAR(10) NOT NULL COMMENT 'язык пользователя',
                                is_alive BOOLEAN NOT NULL COMMENT 'активен ли еще пользователь' DEFAULT True,
                                banned BOOLEAN NOT NULL COMMENT 'забанен пользователь или нет' DEFAULT False
                            );
                            COMMENT ON TABLE users IS 'Таблица с пользователями';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS task_groups(
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(50) NOT NULL COMMENT 'наименование группы',
                                is_active BOOLEAN NOT NULL COMMENT 'активна ли еще группа' DEFAULT True
                            );
                            COMMENT ON TABLE task_groups IS 'Таблица с группами под задачи';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS user_status_varieties(
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(50) NOT NULL COMMENT 'наименование статуса',
                                desc TEXT COMMENT 'подробное описание статуса'
                            );
                            COMMENT ON TABLE user_status_varieties IS 'Справочник статусов пользователей';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS user_group(
                                id SERIAL PRIMARY KEY,
                                user_id BIGINT NOT NULL COMMENT 'id пользователя' REFERENCES users(user_id),
                                task_group_id INT NOT NULL COMMENT 'id группы' REFERENCES task_groups(id),
                                user_status_id INT NOT NULL COMMENT 'статус участника группы' REFERENCES user_status_varieties(id)
                            );
                            COMMENT ON TABLE user_group IS 'Таблица для связки пользователей с группами';
                        """
                    )

                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS task_frequency_varieties(
                                id SERIAL PRIMARY KEY,
                                key VARCHAR(50) NOT NULL COMMENT 'код частотности выполнения задачи',
                                desc VARCHAR(50) COMMENT 'описание частотности'
                            );
                            COMMENT ON TABLE task_frequency_varieties IS 'Справочник частотностей задач';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS tasks(
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(50) NOT NULL COMMENT 'наименование задачи',
                                desc TEXT COMMENT 'подробное описание задачи',
                                creator_id BIGINT NOT NULL COMMENT 'Создатель задачи' REFERENCES users(user_id),
                                executor_id BIGINT NOT NULL COMMENT 'Исполнитель задачи' REFERENCES users(user_id),
                                frequency_id INT NOT NULL COMMENT 'Частотность задачи' REFERENCES task_frequency_varieties(id),
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW() COMMENT 'Дата создания задачи'
                            );
                            COMMENT ON TABLE tasks IS 'Таблица с задачами';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS task_status_varieties(
                                id SERIAL PRIMARY KEY,
                                key VARCHAR(50) NOT NULL COMMENT 'код статуса выполнения задачи',
                                name VARCHAR(50) NOT NULL COMMENT 'наименование статуса выполнения задачи',
                                desc VARCHAR(250) COMMENT 'описание статуса'
                            );
                            COMMENT ON TABLE task_status_varieties IS 'Справочник статусов задач';
                        """
                    )
                    await cursor.execute(
                        query="""
                            CREATE TABLE IF NOT EXISTS task_process(
                                id SERIAL PRIMARY KEY,
                                date_execute TIMESTAMPTZ NOT NULL COMMENT 'Дата, когда нужно выполнить задачу',
                                task_id BIGINT NOT NULL COMMENT 'Задача к выполнению' REFERENCES tasks(id),
                                task_status_id INT NOT NULL COMMENT 'Статус выполнения задачи' REFERENCES task_status_varieties(id)
                            );
                            COMMENT ON TABLE task_process IS 'Таблица со статусами по поставленным задачам';
                        """
                    )
                logger.info("Tables were successfully created")
    except Error as db_error:
        logger.exception("Database error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


asyncio.run(main())
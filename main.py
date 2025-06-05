import asyncio
import logging
import os
import sys

from app.bot import main
from config.config import Config, load_config

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)

asyncio.run(main(config))
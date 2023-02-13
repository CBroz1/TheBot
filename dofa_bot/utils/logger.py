import os
import logging

from dotenv import load_dotenv

from automation.utils.logger import logger, log_format, log_level, stream_handler

load_dotenv()
load_dotenv("TheBot/.env")
DEBUG = os.getenv("BOT_DEBUG")

logger = logging.getLogger(__name__.split(".")[0])
stream_handler.setFormatter(log_format)
logger.setLevel(level=log_level)
logger.handlers = [stream_handler]

# logging.basicConfig(
#     level=logging.DEBUG
#     if os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"
#     else logging.INFO,
#     format=log_format,
# )

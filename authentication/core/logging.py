from logging import getLogger, Logger

from .config import settings

uv_logger = getLogger("uvicorn")
logger = uv_logger.getChild(settings.app_name)


def get_logger(module_name: str) -> Logger:
    return logger.getChild(module_name)

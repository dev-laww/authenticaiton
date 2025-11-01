from logging import getLogger, Logger

from .config import settings

logger = getLogger(settings.app_name)


def get_logger(module_name: str) -> Logger:
    return logger.getChild(module_name)

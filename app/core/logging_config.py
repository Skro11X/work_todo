import sys

from loguru import logger


def setup_logging():
    """
    Настраивает логгер loguru для вывода в консоль с кастомным форматом
    """
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    logger.info("Логгер настроен")

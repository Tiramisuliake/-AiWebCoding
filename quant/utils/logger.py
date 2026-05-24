import sys
from pathlib import Path

from loguru import logger

from config.settings import settings


def setup_logger():
    logger.remove()

    log_dir = Path(__file__).resolve().parent.parent / settings.LOG_DIR
    log_dir.mkdir(exist_ok=True)

    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}"

    logger.add(sys.stderr, level=settings.LOG_LEVEL, format=fmt)
    logger.add(
        log_dir / "quant_{time:YYYY-MM-DD}.log",
        level=settings.LOG_LEVEL,
        format=fmt,
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
    )

    return logger


setup_logger()

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Prevent log messages from propagating to the root logger
    logger.propagate = False

    # Determine backend root dynamically (assuming this file is in backend/app/core)
    BACKEND_ROOT = (
        Path(__file__).resolve().parents[2]
    )  # Points to the 'backend' directory
    LOG_DIR = BACKEND_ROOT / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    # Add handlers only if they don't already exist
    if not any(
        isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    ):
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(console_handler)

    if not any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        # File handler
        file_handler = RotatingFileHandler(
            LOG_DIR / "data_collection.log", maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        )
        logger.addHandler(file_handler)

    return logger

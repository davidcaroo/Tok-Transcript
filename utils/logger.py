"""Logging configuration for Tok-Transcript."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import sys

from utils.paths import get_logs_dir


def setup_logger(name: str = "tok_transcript", level: int = logging.INFO) -> logging.Logger:
    """Set up and return the application logger with rotating file and stream handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Rotating file handler (up to 5MB, keep 3 backups)
    try:
        log_file = get_logs_dir() / "app.log"
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    except Exception as err:
        logger.warning("Could not set up file logger: %s", err)

    return logger

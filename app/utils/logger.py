"""Centralized logging helpers for the AIRA backend."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def build_formatter() -> logging.Formatter:
    """Return the standard application log formatter."""
    return logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)


def create_console_handler(level: int = logging.INFO) -> logging.Handler:
    """Create a console log handler with the standard formatter."""
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(build_formatter())
    return handler


def create_file_handler(
    file_path: str | Path,
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Handler:
    """Create a rotating file handler for persistent logs."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(build_formatter())
    return handler


def get_logger(
    name: str = "aira",
    level: int = logging.INFO,
    log_file: str | Path | None = None,
    include_console: bool = True,
) -> logging.Logger:
    """Return a configured logger with optional console and rotating file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    existing_handler_keys = {
        (type(handler), getattr(handler, "baseFilename", None))
        for handler in logger.handlers
    }

    if include_console and (logging.StreamHandler, None) not in existing_handler_keys:
        logger.addHandler(create_console_handler(level))

    if log_file is not None:
        resolved_log_file = str(Path(log_file).resolve())
        if (RotatingFileHandler, resolved_log_file) not in existing_handler_keys:
            logger.addHandler(create_file_handler(resolved_log_file, level=level))

    return logger

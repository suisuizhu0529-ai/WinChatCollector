"""Logging configuration utilities."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def configure_logging(verbose: bool = False, log_file: Path | None = None) -> None:
    """Configure loguru for command-line inspector tools."""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level, enqueue=False, backtrace=False, diagnose=False)
    if log_file is not None:
        logger.add(log_file, level="DEBUG", rotation="1 MB", retention=3)

"""
Structured logging configuration using structlog + Rich.
Call setup_logging() once at application startup.
"""

import logging
import sys

import structlog
from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging with Rich console output.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure standard library logging with Rich handler
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_path=False,
                omit_repeated_times=False,
            )
        ],
        force=True,
    )

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "langchain", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Get a named structured logger."""
    return structlog.get_logger(name)

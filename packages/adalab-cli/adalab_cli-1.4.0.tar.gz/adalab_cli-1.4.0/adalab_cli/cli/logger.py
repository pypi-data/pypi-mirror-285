"""Submodule for logging messages with different log levels"""

import logging
import os
import sys
from itertools import chain
from types import FrameType
from typing import cast

from loguru import logger

LOG_LEVELS = {
    0: "ERROR",
    1: "WARNING",
    2: "INFO",
    3: "DEBUG",
}

FORMAT = (
    "{level.icon} | <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


class Logger:
    """A custom logger class for logging messages with different log levels."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(
        self, verbosity: int = 0, log_to_file: bool = False, log_file_path: str = "app.log"
    ):
        """
        Initialize the Logger instance.

        :param verbosity: Verbosity level, defaults to 0 (-v).
        :type verbosity: int, optional
        :param log_to_file: Whether to log to a file, defaults to False.
        :type log_to_file: bool, optional
        :param log_file_path: The path to the log file, defaults to "app.log".
        :type log_file_path: str, optional
        """
        if not hasattr(self, "initialized"):  # Ensure __init__ only runs once
            self.handler_id = None
            self.file_handler_id = None

            logger.remove()  # Remove the default logger
            self.set_log_level(verbosity, log_to_file, log_file_path)  # Set the log level
            self.initialized = True

    def set_log_level(
        self, verbosity: int, log_to_file: bool = False, log_file_path: str = "app.log"
    ):
        """
        Set a new log level based on verbosity.

        :param verbosity: Verbosity level (1 for INFO, 2 for DEBUG, 3 for TRACE).
        :type verbosity: int
        """
        log_level = LOG_LEVELS.get(verbosity, "ERROR")
        self.log_level = log_level.upper()
        os.environ["ADALIB_LOG_LEVEL"] = self.log_level

        # The first remove call in __init__ is to remove the default handler.
        # The second remove call here is to remove the previous handler when updating the handler.
        if self.handler_id:
            logger.remove(self.handler_id)  # Remove the previous handler
        self.file_handler_id = logger.add(sink=sys.stdout, format=FORMAT, level=self.log_level)
        setup_loguru_logging_intercept(level=log_level, modules=("adalib", "adalib_auth"))

        if log_to_file:
            if self.file_handler_id:
                logger.remove(self.file_handler_id)  # Remove the previous file handler
            logger.add(log_file_path, level=self.log_level, format=FORMAT)

    @staticmethod
    def from_env():
        """
        Create a Logger instance with settings from environment variables.

        :return: A configured Logger instance.
        :rtype: Logger
        """
        verbosity = int(os.getenv("VERBOSITY", "1"))
        log_to_file = os.getenv("LOG_TO_FILE", "False").lower() in ("true", "1", "yes")
        log_file_path = os.getenv("LOG_FILE_PATH", "app.log")
        return Logger(verbosity, log_to_file, log_file_path)


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 7
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1
        logger_with_opts = logger.opt(depth=depth, exception=record.exc_info)
        try:
            logger_with_opts.log(level, "{}", record.getMessage())
        except Exception as e:
            safe_msg = getattr(record, "msg", None) or str(record)
            logger_with_opts.warning(
                "Exception logging the following native logger message: {}, {!r}", safe_msg, e
            )


def setup_loguru_logging_intercept(level=logging.DEBUG, modules=()):
    logging.basicConfig(handlers=[InterceptHandler()], level=level)  # noqa
    for logger_name in chain(("",), modules):
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=level)]
        mod_logger.propagate = False

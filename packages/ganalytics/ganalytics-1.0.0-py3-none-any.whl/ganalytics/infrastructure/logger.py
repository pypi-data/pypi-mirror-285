"""Implementation of the logger module."""
import logging
from logging import LogRecord

import coloredlogs

from src.ganalytics.interfaces.ilogger import ILogger



class ContextFilter(logging.Filter):
    """Logging filter for adding context to log records."""

    def filter(self, record: LogRecord) -> bool:
        # Get the current frame and backtrack to the caller's frame
        frame = logging.currentframe()
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
        # Get the caller's frame
        caller_frame = frame.f_back
        # Get the caller's module name
        record.module = caller_frame.f_globals["__name__"]
        # Get the caller's line number
        record.lineno = caller_frame.f_lineno
        return True


class Logger(ILogger):
    """Logger Implementation"""

    def __init__(self):
        """Initialize the Logger"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        simple = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        verbose = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(module)s - %(lineno)d"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(verbose)
        self.logger.addHandler(console_handler)

        # Add the context filter
        self.logger.addFilter(ContextFilter())

        coloredlogs.install(level="DEBUG", logger=self.logger)

    def info(self, message: str):
        """Log a message"""
        self.logger.info(message)

    def error(self, message: str):
        """Log an error"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log a warning"""
        self.logger.warning(message)
"""
Logging abstraction and implementations.

All logging goes through this interface.
Easy to mock, easy to redirect output.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import logging
import sys


class Logger(ABC):
    """
    Logging interface.

    Application code depends on this, not on logging module directly.
    """

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message."""
        ...

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message."""
        ...

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message."""
        ...

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message."""
        ...

    @abstractmethod
    def exception(self, exc: Exception, message: str = '') -> None:
        """Log exception with traceback."""
        ...


class FileLogger(Logger):
    """Write logs to a file."""

    def __init__(self, log_file: Path):
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(str(log_file))
        self._logger.handlers.clear()  # Remove any existing handlers

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def exception(self, exc: Exception, message: str = '') -> None:
        self._logger.exception(message or str(exc))


class ConsoleLogger(Logger):
    """Write logs to console (stdout/stderr)."""

    def debug(self, message: str) -> None:
        pass  # Don't spam console with debug

    def info(self, message: str) -> None:
        print(f"INFO: {message}")

    def warning(self, message: str) -> None:
        print(f"WARNING: {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        print(f"ERROR: {message}", file=sys.stderr)

    def exception(self, exc: Exception, message: str = '') -> None:
        print(f"ERROR: {message or str(exc)}", file=sys.stderr)


class CompositeLogger(Logger):
    """Write to multiple loggers simultaneously."""

    def __init__(self, loggers: list[Logger]):
        self._loggers = loggers

    def debug(self, message: str) -> None:
        for logger in self._loggers:
            logger.debug(message)

    def info(self, message: str) -> None:
        for logger in self._loggers:
            logger.info(message)

    def warning(self, message: str) -> None:
        for logger in self._loggers:
            logger.warning(message)

    def error(self, message: str) -> None:
        for logger in self._loggers:
            logger.error(message)

    def exception(self, exc: Exception, message: str = '') -> None:
        for logger in self._loggers:
            logger.exception(exc, message)


class NoOpLogger(Logger):
    """Logger that does nothing (for testing)."""

    def debug(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def exception(self, exc: Exception, message: str = '') -> None:
        pass

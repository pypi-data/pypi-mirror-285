from __future__ import annotations

from abc import ABC, abstractmethod

from ._contexts import Context


class ContextLogger(ABC):
    @abstractmethod
    def add_context(self, context: Context):
        """
        This add the context to the logger.

        Setting a key already existing should override the old value.
        """

    @abstractmethod
    def copy(self, name: str) -> ContextLogger:
        """
        This method will create a new logger with the same context as the current one.
        The name of the logger will be the same as the current one with the name parameter added to it.

        This should create a deep copy of the logger.
        """

    @abstractmethod
    def debug(self, msg: str, **logger_kwargs):
        """
        This will log a debug message to the logger.
        """

    @abstractmethod
    def info(self, msg: str, **logger_kwargs):
        """
        This will log an info message to the logger.
        """

    @abstractmethod
    def warning(self, msg: str, **logger_kwargs):
        """
        This will log a warning message to the logger.
        """

    @abstractmethod
    def error(self, msg: str, **logger_kwargs):
        """
        This will log an error message to the logger.
        """

    @abstractmethod
    def critical(self, msg: str, **logger_kwargs):
        """
        This will log a critical message to the logger.
        """

    def exception(self, msg: str, **logger_kwargs):
        """
        This will log an exception message to the logger.
        """

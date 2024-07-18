import logging

from ._context_logger import ContextLogger
from ._contexts import Context


class V1ContextLogger(ContextLogger):
    def __init__(self, logger: logging.Logger):
        self.__logger = logger
        self.__context = {}

    def add_context(self, context: Context):
        self.__context.update(context.get_context())

    def copy(self, name: str) -> ContextLogger:
        copy_logger = V1ContextLogger(logging.getLogger('.'.join([self.__logger.name, name])))
        copy_logger.__context = self.__context.copy()
        return copy_logger

    def debug(self, msg: str, **logger_kwargs):
        self.__logger.debug(msg=msg, extra=self.__context, **logger_kwargs)

    def info(self, msg: str, **logger_kwargs):
        self.__logger.info(msg=msg, extra=self.__context, **logger_kwargs)

    def warning(self, msg: str, **logger_kwargs):
        self.__logger.warning(msg=msg, extra=self.__context, **logger_kwargs)

    def error(self, msg: str, **logger_kwargs):
        self.__logger.error(msg=msg, extra=self.__context, **logger_kwargs)

    def critical(self, msg: str, **logger_kwargs):
        self.__logger.critical(msg=msg, extra=self.__context, **logger_kwargs)

    def exception(self, msg: str, **logger_kwargs):
        self.__logger.exception(msg=msg, extra=self.__context, **logger_kwargs)

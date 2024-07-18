import logging
import sys
from copy import copy
from typing import Literal

from ._format import Color, Format

TRACE_LOG_LEVEL = 5


class DefaultFormatter(logging.Formatter):
    level_colors = {
        TRACE_LOG_LEVEL: Color.BLUE,
        logging.DEBUG: Color.CYAN,
        logging.INFO: Color.GREEN,
        logging.WARNING: Color.YELLOW,
        logging.ERROR: Color.LIGHTRED_EX,
        logging.CRITICAL: Color.RED,
    }
    default_fmt = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'

    def __init__(
        self,
        fmt: str | None = default_fmt,
        datefmt: str | None = None,
        style: Literal['%', '{', '$'] = '%',
    ):
        self.use_colors = sys.stdout.isatty()

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        color = self.level_colors.get(level_no)

        return Format.color(level_name, color)

    def formatMessage(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)
        level_name = record_copy.levelname

        if self.use_colors:
            level_name = self.color_level_name(level_name, record_copy.levelno)

        record_copy.__dict__['levelname'] = level_name

        return super().formatMessage(record_copy)

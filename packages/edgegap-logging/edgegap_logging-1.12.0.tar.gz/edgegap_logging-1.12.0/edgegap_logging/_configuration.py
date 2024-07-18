import os

from pydantic import BaseModel

log_format = os.environ.get('LOG_FORMAT', '%(asctime)s | %(levelname)s | %(name)s | %(message)s')
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()


class LoggingConfiguration(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        'default': {
            '()': 'edgegap_logging.DefaultFormatter',
            'fmt': log_format,
        },
    }
    handlers: dict = {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    }
    loggers: dict = {
        'root': {
            'handlers': ['default'],
            'level': log_level,
        },
    }
    root: dict = {
        'level': log_level,
        'handlers': ['default'],
    }

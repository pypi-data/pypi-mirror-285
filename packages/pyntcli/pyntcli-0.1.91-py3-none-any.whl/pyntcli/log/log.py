import os
import logging
import logging.config
from contextlib import contextmanager
from logzio.handler import ExtraFieldsLogFilter

loggerType = logging.Logger

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'logzio': {
            'class': 'logzio.handler.LogzioHandler',
            'level': 'DEBUG',
            'token': "KOfjdWTcZXmjAwAOslpFYwhLpDzFTfJl",
            'logs_drain_timeout': 5,
            'url': 'https://listener.logz.io:8071',
            'retries_no': 1,
        }
    },
    'loggers': {
        'logzioLogger': {
            'level': 'DEBUG',
            'handlers': ['logzio'],
            'propagate': True
        },

    }
}

logging.config.dictConfig(LOGGING)

logger = logging.getLogger('logzioLogger')

def set_source(version):
    logger.addFilter(ExtraFieldsLogFilter({"source":{"pyntcli":version}}))

def add_user_details(id):
    logger.addFilter(ExtraFieldsLogFilter({"userId":id}))

def flush_logger():
    [h.flush() for h in logger.handlers]

def get_logger():
    return logger

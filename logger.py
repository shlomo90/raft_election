import os
import logging


CUR_FILE_PATH = os.path.abspath(__file__)
CUR_FILE_DIR = os.path.dirname(CUR_FILE_PATH)
LOG_DIR_PATH = CUR_FILE_DIR + '/logs'
LOG_PATH = LOG_DIR_PATH + '/error.log'

DEFAULT_FORMAT_STR = '%(asctime)s %(levelname)5s %(name)s %(message)s'
DEFAULT_LOG_LEVEL = logging.DEBUG
_LOGGERS = {}


def getlogger(name):
    global _LOGGERS
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)

    handler = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter(DEFAULT_FORMAT_STR)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    _LOGGERS[name] = logger
    return logger

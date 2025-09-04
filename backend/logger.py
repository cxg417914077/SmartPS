import time
import uuid
import datetime
import logging.config

from backend.app.core.config import settings


def set_trace_id(trace_id: str = None):
    trace_id = trace_id or uuid.uuid4().hex
    settings.REQUEST_ID_CONTEXT.set(trace_id)


def get_trace_id() -> str:
    trace_id = settings.REQUEST_ID_CONTEXT.get()
    if not trace_id or trace_id == "-":
        trace_id = uuid.uuid4().hex
        set_trace_id(trace_id)
    return trace_id


def beijing_time_converter(sec, what):
    timezone_offset = 0  # 默认不偏移
    if time.timezone == 0:  # 当系统为UTC时间时，偏移成北京时间
        timezone_offset = 8
    beijing_time = datetime.datetime.now() + datetime.timedelta(hours=timezone_offset)
    beijing_time = beijing_time.timestamp()
    return time.localtime(beijing_time)


class ContextFilter:
    def __init__(self, pass_level):
        self.pass_level = pass_level

    def filter(self, record):
        record.request_id = get_trace_id()
        return True


logging_config = {
    'version': 1,
    'incremental': False,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'class': 'logging.Formatter',
            'format': '+ %(asctime)s.%(msecs)03dZ %(levelname)s <%(module)s> {%(request_id)s} | %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    "filters": {
        "filter_request_id": {
            '()': ContextFilter,
            "pass_level": logging.DEBUG
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "filters": ["filter_request_id", ]
        },

        "api": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",  # root log level 为info时, 不会输出debug日志
            "formatter": "default",
            "filename": settings.LOG_PATH,
            'mode': 'a+',
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 20,
            "encoding": "utf8",
            "filters": ["filter_request_id", ]
        },
    },
    'root': {
        'level': settings.LOG_LEVEL,
        'handlers': ['console', 'api'],
    },
}

logging.config.dictConfig(logging_config)
logging.Formatter.converter, logger = beijing_time_converter, logging.getLogger("default")
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("aioboto3").setLevel(logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
"""
A Colorful AWS SDK wrapper for Python
github.com/Hotmart-Org/pinkboto
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime
from .aws import aws
from .utils import to_csv, to_unix_epoch
from .cache import Cache


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """https://pypi.org/project/python-json-logger"""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


logger = logging.getLogger("pinkboto")
logHandler = logging.StreamHandler(stream=sys.stderr)
formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger.setLevel(logging.ERROR)
logger.addHandler(logHandler)
logger.propagate = True

__all__ = aws, to_csv, to_unix_epoch, Cache

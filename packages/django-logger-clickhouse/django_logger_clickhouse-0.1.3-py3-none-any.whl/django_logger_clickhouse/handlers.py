import io
import logging
import traceback
from uuid import uuid4
import datetime
import json

from .tasks import record_in_clickhouse


class ClickHouseLogger():
    def format_exception(ei) -> str:
        sio = io.StringIO()
        tb = ei[2]
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s

    def logger(record: logging.LogRecord = "") -> None:
        data = {}
        data["uuid"] = str(uuid4())
        data["created_dt"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f")
        data["pathname"] = str(getattr(record, "pathname", ""))
        data["funcName"] = str(getattr(record, "funcName", ""))
        data["lineno"] = getattr(record, "lineno", 0)
        data["message"] = record.getMessage()
        data["exc_text"] = str(getattr(record, "exc_text", ""))
        data["created"] = getattr(record, "lineno", 0)
        data["filename"] = str(getattr(record, "filename", ""))
        data["levelname"] = str(getattr(record, "levelname", ""))
        data["levelno"] = str(getattr(record, "levelno", ""))
        data["module"] = str(getattr(record, "module", ""))
        data["msecs"] = getattr(record, "msecs", 0)
        data["msg"] = str(getattr(record, "msg", ""))
        data["name"] = str(getattr(record, "name", ""))
        data["process"] = str(getattr(record, "process", ""))
        data["processName"] = str(getattr(record, "processName", ""))
        data["relativeCreated"] = str(getattr(record, "relativeCreated", ""))
        data["stack_info"] = str(getattr(record, "stack_info", ""))
        data["thread"] = str(getattr(record, "thread", ""))
        data["threadName"] = str(getattr(record, "threadName", ""))
        if data["msg"] == '%s: %s':
            data["msg"] = data["exc_text"]
        return json.dumps(data)


class LoggerHandler(logging.StreamHandler):

    def emit(self, record) -> None:
        if isinstance(record, logging.LogRecord):
            try:
                if record.exc_info:  # Check if exception info exists
                    record.exc_text = "".join(traceback.format_exception(
                        *record.exc_info))  # Format exception info
                data = ClickHouseLogger.logger(record)
                record_in_clickhouse.delay(data, 'logs')
            except Exception as e:
                logging.exception(f"django-clickhouse-logger [ERROR] {e}")

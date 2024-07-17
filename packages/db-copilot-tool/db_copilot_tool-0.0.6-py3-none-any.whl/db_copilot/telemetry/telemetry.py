"""File for the LoggingPrintHandler Class."""
from datetime import datetime
import inspect
import logging
import os
import sys
import traceback
import uuid
from contextlib import contextmanager
from functools import wraps
import pkg_resources


from .activity import ActivityLoggerAdapter
from .activity import log_activity as _log_activity

try:
    db_copilot_version = pkg_resources.get_distribution("dbcopilot").version
except Exception:
    db_copilot_version = ""

default_custom_dimensions = {
    "db_copilot_version": db_copilot_version,
}

DEFAULT_ACTIVITY_TYPE = "InternalCall"
STACK_FMT = "%s, line %d in function %s."
CORRELATION_ID = "x-ms-correlation-id"

@contextmanager
def _run_without_logging(logger, activity_name, activity_type, custom_dimensions):
    yield ActivityLoggerAdapter(logger, {"activity_name": activity_name})


class LoggerFactory:
    """Factory for creating loggers"""

    def __init__(self, stdout=False):
        """Initialize the logger factory"""
        self.loggers = {}
        self.stdout = stdout
        self.appinsights = None

    def add_handler(self, handler):
        logger = logging.root
        logger.addHandler(handler)

    def with_stdout(self, stdout=True):
        """Set whether to log to stdout"""
        self.stdout = stdout
        # Add stdout handler to any loggers created before enabling stdout.
        for logger in self.loggers.values():
            if self.stdout:
                stdout_handler = logging.StreamHandler(stream=sys.stdout)
                stdout_handler.setFormatter(
                    logging.Formatter(
                        "[%(asctime)s][%(levelname)-8s][%(name)s][%(threadName)s] - %(message)s (%(filename)s:%(lineno)s)",
                        "%Y-%m-%d %H:%M:%S",
                    )
                )
                logger.addHandler(stdout_handler)
        return self

    def with_appinsights(self, appinsights_connection_string=None):
        """Set whether to log track_* events to appinsights"""
        try:
            from opencensus.ext.azure.log_exporter import AzureEventHandler
            if appinsights_connection_string:
                self.appinsights = AzureEventHandler(
                    connection_string=appinsights_connection_string
                )
            else:
                # Read from environment variable
                self.appinsights = AzureEventHandler()
        except ImportError:
            raise Exception("Please install opencensus-ext-azure to use appinsights")

    def get_logger(self, name, level=logging.INFO):
        """Get a logger with the given name and level"""
        if name not in self.loggers:
            logger = logging.getLogger(f"db_copilot.{name}")
            logger.setLevel(level)
            if self.stdout:
                stdout_handler = logging.StreamHandler(stream=sys.stdout)
                stdout_handler.setFormatter(
                    logging.Formatter(
                        "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s (%(filename)s:%(lineno)s)",
                        "%Y-%m-%d %H:%M:%S",
                    )
                )
                logger.addHandler(stdout_handler)
            self.loggers[name] = logger
        return self.loggers[name]

    def track_activity(
        self,
        logger,
        name,
        activity_type=DEFAULT_ACTIVITY_TYPE,
        custom_dimensions=None,
    ):
        """Track the activity of the given logger"""
        if self.appinsights:
            logging.info(f"Tracking activity: {name}. appinsights: {self.appinsights}")
            stack = self.get_stack()
            custom_dimensions = custom_dimensions if custom_dimensions is not None else {}
            custom_dimensions.update({**default_custom_dimensions, "trace": stack})

            child_logger = logger.getChild(name)
            child_logger.addHandler(self.appinsights)
            return _log_activity(child_logger, name, activity_type, custom_dimensions)
        else:
            logging.info("AppInsights is not enabled. Skipping tracking activity.")
            return _run_without_logging(logger, name, activity_type, custom_dimensions)

    def telemetry_info(self, logger, message, custom_dimensions=None):
        """Track info with given logger"""
        if self.appinsights:
            payload = custom_dimensions
            payload.update(default_custom_dimensions)
            child_logger = logger.getChild("appinsights")
            child_logger.addHandler(self.appinsights)
            if ActivityLoggerAdapter:
                activity_logger = ActivityLoggerAdapter(child_logger, payload)
                activity_logger.info(message)

    def telemetry_error(self, logger, message, custom_dimensions=None):
        """Track error with given logger"""
        if self.appinsights:
            payload = custom_dimensions
            payload.update(default_custom_dimensions)
            child_logger = logger.getChild("appinsights")
            child_logger.addHandler(self.appinsights)
            if ActivityLoggerAdapter:
                activity_logger = ActivityLoggerAdapter(child_logger, payload)
                activity_logger.error(message)

    @staticmethod
    def get_stack(limit=3, start=1) -> str:
        """Get the stack trace as a string"""
        try:
            stack = inspect.stack()
            # The index of the first frame to print.
            begin = start + 2
            # The index of the last frame to print.
            if limit:
                end = min(begin + limit, len(stack))
            else:
                end = len(stack)

            lines = []
            for frame in stack[begin:end]:
                file, line, func = frame.filename, frame.lineno, frame.function
                parts = file.rsplit("\\", 4)
                parts = parts if len(parts) > 1 else file.rsplit("/", 4)
                file = "|".join(parts[-3:])
                lines.append(STACK_FMT % (file, line, func))
            return "\n".join(lines)
        except Exception:
            pass
        return None

_logger_factory = LoggerFactory()

def enable_stdout_logging():
    """Enable logging to stdout"""
    _logger_factory.with_stdout(True)

def add_handler(handler):
    """Add handler to all loggers"""
    _logger_factory.add_handler(handler)


def enable_appinsights_logging(appinsights_conn_string: str=None):
    """Enable logging to appinsights"""
    _logger_factory.with_appinsights(appinsights_connection_string=appinsights_conn_string)


def get_logger(name, level=logging.INFO) -> logging.Logger:
    """Get a logger with the given name and level"""
    return _logger_factory.get_logger(name, level)


def track_info(message, logger=None, custom_dimensions={}):
    """Track info with given logger"""
    if logger is None:
        logger = get_logger("track_info", level=logging.INFO)
    return _logger_factory.telemetry_info(logger, message, custom_dimensions)


def track_error(message, logger=None, custom_dimensions={}):
    """Track error with given logger"""
    if logger is None:
        logger = get_logger("track_error", level=logging.ERROR)
    return _logger_factory.telemetry_error(logger, message, custom_dimensions)


def track_activity(
    logger,
    name,
    activity_type=DEFAULT_ACTIVITY_TYPE,
    custom_dimensions=None,
):
    """Track the activity with given logger"""
    return _logger_factory.track_activity(
        logger, name, activity_type, custom_dimensions
    )


def track_function(logger=None, name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_activity(
                logger or get_logger("db_copilot_tool"), name or func.__name__
            ) as activity_logger:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    except_stacks = traceback.TracebackException.from_exception(ex)
                    lines = []
                    for frame in except_stacks.stack:
                        file, line, func_name = frame.filename, frame.lineno, frame.name
                        parts = file.rsplit("\\", 4)
                        parts = parts if len(parts) > 1 else file.rsplit("/", 4)
                        file = "|".join(parts[-3:])
                        lines.append(STACK_FMT % (file, line, func_name))
                    activity_logger.activity_info["exception"] = "\n".join(lines)
                    raise ex

        return wrapper

    return decorator


class RequestFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        try:
            request_id = get_correlation_id()
            if not request_id:
                request_id = uuid.uuid4()
            lines = []
            line_number = 0
            for line in result.split("\n"):
                if line_number > 0:
                    line = f"[{request_id}] [{line_number:>3}] {line}"
                else:
                    line = f"[{request_id}] {line}"
                lines.append(line)
                line_number += 1
            return "\n".join(lines)
        except:
            pass
        return result


class LoggingPrintHandler(logging.Handler):
    """A handler class which allows the cursor to stay on one line for selected messages."""

    def emit(self, record):
        """emit."""
        try:
            msg = self.format(record)
            print(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def set_print_logger(level=logging.INFO):
    """set_logger."""
    # logger = logging.getLogger('dbcopilot')
    logger = logging.root
    logger.setLevel(level)
    if [h for h in logger.handlers if isinstance(h, LoggingPrintHandler)]:
        return
    handler = LoggingPrintHandler()
    formatter = RequestFormatter("[%(asctime)s] [%(levelname)s] [%(name)s.%(module)s:%(lineno)d] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def set_file_logger(log_path: str, level=logging.INFO, mode: str='a'):
    logger = logging.root
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_path, mode=mode)  
    file_handler.setLevel(logging.DEBUG)  
    file_handler.setFormatter(RequestFormatter("[%(asctime)s] [%(levelname)s] [%(name)s.%(module)s:%(lineno)d] %(message)s"))
    logger.addHandler(file_handler)


def get_correlation_id():    
    from flask import request, has_request_context, g
    if has_request_context():
        if hasattr(g, CORRELATION_ID):
            return getattr(g, CORRELATION_ID)
        return request.headers.get(CORRELATION_ID, None)
    return None
    
def set_correlation_id(id):
    from flask import has_request_context, g
    assert has_request_context()
    setattr(g, CORRELATION_ID, id)

class LatencyTracker:
    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, *args):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
"""File for the LoggingPrintHandler Class."""

import inspect
import logging
import os
import sys
import traceback
import uuid
from contextlib import contextmanager
from functools import lru_cache, wraps

import pkg_resources
from azureml.telemetry import INSTRUMENTATION_KEY, get_telemetry_log_handler
from azureml.telemetry.activity import ActivityLoggerAdapter
from azureml.telemetry.activity import log_activity as _log_activity

STACK_FMT = "%s, line %d in function %s."
COMPONENT_NAME = "db_copilot_tool"
instrumentation_key = INSTRUMENTATION_KEY
try:
    version = pkg_resources.get_distribution("db_copilot_tool").version
except Exception:
    version = ""

default_custom_dimensions = {
    "source": COMPONENT_NAME,
    "version": version,
}
current_folder = os.path.dirname(os.path.realpath(__file__))
telemetry_config_path = os.path.join(current_folder, "_telemetry.json")

telemetry_enabled = True
DEFAULT_ACTIVITY_TYPE = "InternalCall"


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
        self.with_appinsights()

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

    def with_appinsights(self):
        """Set whether to log track_* events to appinsights"""
        if telemetry_enabled:
            import atexit

            self.appinsights = get_telemetry_log_handler(
                instrumentation_key=instrumentation_key,
                component_name=COMPONENT_NAME,
                path=telemetry_config_path,
            )
            atexit.register(self.appinsights.flush)

    def get_logger(self, name, level=logging.INFO):
        """Get a logger with the given name and level"""
        if name not in self.loggers:
            logger = logging.getLogger(f"db_copilot_tool.{name}")
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
        custom_dimensions={},
    ):
        """Track the activity of the given logger"""
        if self.appinsights:
            logging.info(f"Tracking activity: {name}. appinsights: {self.appinsights}")
            stack = self.get_stack()
            custom_dimensions.update({**default_custom_dimensions, "trace": stack})
            run_info = self._try_get_run_info()
            if run_info is not None:
                custom_dimensions.update(run_info)
            child_logger = logger.getChild(name)
            child_logger.addHandler(self.appinsights)
            return _log_activity(child_logger, name, activity_type, custom_dimensions)
        else:
            logging.info("AppInsights is not enabled. Skipping tracking activity.")
            return _run_without_logging(logger, name, activity_type, custom_dimensions)

    def telemetry_info(self, logger, message, custom_dimensions={}):
        """Track info with given logger"""
        if self.appinsights:
            payload = custom_dimensions
            payload.update(default_custom_dimensions)
            child_logger = logger.getChild("appinsights")
            child_logger.addHandler(self.appinsights)
            if ActivityLoggerAdapter:
                activity_logger = ActivityLoggerAdapter(child_logger, payload)
                activity_logger.info(message)

    def telemetry_error(self, logger, message, custom_dimensions={}):
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

    @staticmethod
    @lru_cache(maxsize=1)
    def _try_get_run_info():
        info = {
            "subscription": os.environ.get("AZUREML_ARM_SUBSCRIPTION", ""),
            "run_id": os.environ.get("AZUREML_RUN_ID", ""),
            "resource_group": os.environ.get("AZUREML_ARM_RESOURCEGROUP", ""),
            "workspace_name": os.environ.get("AZUREML_ARM_WORKSPACE_NAME", ""),
            "experiment_id": os.environ.get("AZUREML_EXPERIMENT_ID", ""),
        }
        try:
            import re

            location = os.environ.get("AZUREML_SERVICE_ENDPOINT")
            location = re.compile("//(.*?)\\.").search(location).group(1)
        except Exception:
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT", "")
        info["location"] = location
        try:
            from azureml.core import Run

            run: Run = Run.get_context()
            if hasattr(run, "experiment"):
                info["parent_run_id"] = run.properties.get(
                    "azureml.pipelinerunid", "Unknown"
                )
                info["mlIndexAssetKind"] = run.properties.get(
                    "azureml.mlIndexAssetKind", "Unknown"
                )
                info["mlIndexAssetSource"] = run.properties.get(
                    "azureml.mlIndexAssetSource", "Unknown"
                )
                module_name = run.properties.get("azureml.moduleName", "Unknown")
                info["moduleName"] = (
                    module_name
                    if module_name.startswith("db_copilot")
                    or module_name.startswith("llm_")
                    else "Unknown"
                )
                if info["moduleName"] != "Unknown":
                    module_id = run.properties.get("azureml.moduleid", "Unknown")
                    if module_id != "Unknown":
                        version_info = module_id.split("/")[-1]
                        info["moduleVersion"] = version_info
                    else:
                        info["moduleVersion"] = "Unknown"
        except Exception:
            pass
        return info


_logger_factory = LoggerFactory()


def enable_stdout_logging():
    """Enable logging to stdout"""
    _logger_factory.with_stdout(True)


def enable_appinsights_logging():
    """Enable logging to appinsights"""
    _logger_factory.with_appinsights()


def get_logger(name, level=logging.INFO):
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
    custom_dimensions={},
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
            from flask import has_request_context, request

            if has_request_context():
                request_id = request.headers.get("x-request-id", None)
            else:
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
    formatter = RequestFormatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s.%(module)s:%(lineno)d] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

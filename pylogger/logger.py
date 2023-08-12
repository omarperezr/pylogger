import ast
import json
import sys
import traceback
from datetime import datetime
from distutils.util import strtobool
from typing import Callable, Union

import loguru

from config_manager.config_manager import config_manager
from config_manager.env_var import EnvVar
from pylogger import log_levels
from pylogger.handlers.file_handler import file_handler
from pylogger.handlers.gcp_handler import get_gcp_handler
from utils import dates, function_execution_timer, hardware_metrics


class Logger:
    """Provides methods to log messages and exceptions at different log levels.
    It uses the loguru library for logging.

    Attributes:
        None

    Methods:
        log_execution_time: A decorator method that logs the execution time of a function.
        error: Logs an exception at the ERROR log level.
        warn: Logs an exception at the WARN log level.
        critical_error: Logs an exception at the CRITICAL log level.
        info: Logs a custom message at the INFO log level.

    Example usage:
        Logger.info("Custom message", {"extra_args": {"key": "value"}})
        @Logger.log_execution_time
        def my_function():
            # Function code here
            pass
    """

    all_handlers = {
        "stdout": {"sink": sys.stdout, "format": "<lvl>{message}</lvl>"},
        "gcp": get_gcp_handler("logger_log_file"),
        "file": {"sink": file_handler, "format": "<lvl>{message}</lvl>"},
    }

    handlers_to_use = list()
    for handler in ast.literal_eval(config_manager.get("Logger", "handlers")):
        handler_value = all_handlers.get(handler)
        if handler_value is not None:
            handlers_to_use.append(handler_value)

    _LOGURU_CONFIG = {
        "handlers": [handler for handler in handlers_to_use],
        "levels": [  # Custom log levels
            {"name": log_levels.WARN, "no": 30, "color": "<yellow><bold>"}
        ],
    }
    _BEAUTIFY_JSON_LOGS = strtobool(str(EnvVar("BEAUTIFY_JSON_LOGS", "False")))

    loguru.logger.configure(**_LOGURU_CONFIG)

    @staticmethod
    def log_execution_time(function: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            timed_result = function_execution_timer.execute_timed(
                function, *args, **kwargs
            )
            Logger._log_function_execution_time(
                function,
                timed_result["start_timestamp"],
                timed_result["end_timestamp"],
                timed_result["execution_time_ms"],
            )
            return timed_result["result"]

        return wrapper

    @staticmethod
    def _log_exception(exception: Exception, type: str, level: str) -> None:
        log = Logger._get_base_log(type, level)
        log["exc_info"] = traceback.format_exc()
        log["message"] = str(exception)
        log["data"] = {"exception_type": exception.__class__.__name__}
        Logger._log(log)

    @staticmethod
    def error(exception: Exception) -> None:
        Logger._log_exception(exception, "error", log_levels.ERROR)

    @staticmethod
    def warn(exception: Exception) -> None:
        Logger._log_exception(exception, "warn", log_levels.WARN)

    @staticmethod
    def critical_error(exception: Exception) -> None:
        log = Logger._get_base_log("critical_error", log_levels.CRITICAL)
        log["exc_info"] = traceback.format_exc()
        log["message"] = str(exception)
        log["data"] = {"exception_type": exception.__class__.__name__}
        Logger._log(log)

    @staticmethod
    def info(message: str, extra_args: dict = {}) -> None:
        log = Logger._get_base_log("custom_message", log_levels.INFO)
        log["message"] = message
        log["data"] = {"extra_args": extra_args}
        Logger._log(log)

    @staticmethod
    def _log_function_execution_time(
        function: Callable,
        start: datetime,
        end: datetime,
        execution_time_ms: int,
    ) -> None:
        log = Logger._get_base_log("execution_time", log_levels.INFO)
        log["execution_time_ms"] = execution_time_ms
        log["data"] = {
            "start_timestamp": dates.to_utc_isostring(start),
            "end_timestamp": dates.to_utc_isostring(end),
            "module": function.__module__,
            "function": function.__name__,
            "full_name": f"{function.__module__}.{function.__name__}",
        }
        Logger._log(log)

    @staticmethod
    def _log(log: dict) -> None:
        Logger._register_log(log)

    @staticmethod
    def _get_base_log(log_type: str, level: str) -> dict:
        base_log = {
            "project": str(EnvVar("PROJECT")),
            "version": str(EnvVar("PROJECT_VERSION")),
            "repository": str(EnvVar("PROJECT_REPOSITORY")),
            "environment": str(EnvVar("ENVIRONMENT")),
            "service": str(EnvVar("SERVICE")),
            "num_cpu_cores": hardware_metrics.get_available_cpu_count(),
            "type": log_type,
            "timestamp": Logger._get_timestamp(),
            "levelname": level,
            "data": {},
        }

        return base_log

    @staticmethod
    def _get_json_indent() -> Union[int, None]:
        return 2 if Logger._BEAUTIFY_JSON_LOGS else None

    @staticmethod
    def _register_log(json_log: dict) -> None:
        loguru.logger.log(
            json_log["levelname"],
            json.dumps(json_log, indent=Logger._get_json_indent()),
        )

    @staticmethod
    def _get_timestamp() -> str:
        return dates.to_utc_isostring(dates.now())

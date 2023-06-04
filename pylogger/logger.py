import functools
import json
import sys
import traceback
from copy import deepcopy
from datetime import datetime
from distutils.util import strtobool
from typing import Callable, List, Optional, Union

import loguru
from django.http import HttpResponse
from rest_framework.request import Request

from config.config_provider import ConfigProvider
from exceptions.http_exception import HTTPException
from pylogger import log_levels
from utils import dates, function_execution_timer, hardware_metrics
from utils.http_response import is_success_response
from utils.json_cleaner import JSONCleaner


class Logger:
    _ROUTE_BODY_ATTRS_TO_IGNORE = []

    _LOGURU_CONFIG = {
        "handlers": [
            {"sink": sys.stdout, "format": "<lvl>{message}</lvl>"},
        ],
        "levels": [  # Custom log levels
            {"name": log_levels.WARN, "no": 30, "color": "<yellow><bold>"}
        ],
    }

    _REQUEST_LOGS_ATTR_NAME = "logs"
    _BEAUTIFY_JSON_LOGS = strtobool(
        ConfigProvider.get_env_var("BEAUTIFY_JSON_LOGS", str(False))
    )

    def __init__(self):
        # loguru.logger.configure(**Logger._LOGURU_CONFIG)
        loguru.logger.configure(**ConfigProvider.get_logger_config()["loguru"])

    @staticmethod
    def log_execution_time(function: Callable) -> Callable:
        functools.wraps(function)

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
    def log_request(request: Request, log_body: bool = True) -> None:
        log = Logger._get_base_log("request", log_levels.INFO, request)
        log["data"] = {
            "body": Logger._get_cleaned_request_body(request) if log_body else None
        }
        Logger._log(log)

    @staticmethod
    def log_response(
        response: HttpResponse,
        execution_time_ms: int,
        request: Request,
        log_body: bool = True,
    ) -> None:
        level = log_levels.INFO if is_success_response(response) else log_levels.ERROR
        log = Logger._get_base_log("response", level, request)
        log["execution_time_ms"] = execution_time_ms
        if not is_success_response(response):
            log["exc_info"] = (
                getattr(request, "last_exc_info")
                if hasattr(request, "last_exc_info")
                else None
            )
        log["data"] = {
            "status_code": response.status_code,
            "body": response.content.decode("utf-8") if log_body else None,
            "content_type": response.headers.get("Content-Type"),
            "request_body": Logger._get_cleaned_request_body(request)
            if not is_success_response(response)
            else None,
        }
        Logger._log(log)

    @staticmethod
    def _log_exception(
        exception: Exception, type: str, level: str, request: Request = None
    ) -> None:
        log = Logger._get_base_log(type, level, request)
        log["exc_info"] = traceback.format_exc()
        # Store last exception stack trace in request to obtain it in response
        Logger._register_last_exception(log["exc_info"], request)
        log["message"] = str(exception)
        log["data"] = {"exception_type": exception.__class__.__name__}
        if isinstance(exception, HTTPException):
            log["data"]["status_code"] = exception.status_code
        Logger._log(log)

    @staticmethod
    def error(exception: Exception, request: Request = None) -> None:
        Logger._log_exception(exception, "error", log_levels.ERROR, request)

    @staticmethod
    def warn(exception: Exception, request: Request = None) -> None:
        Logger._log_exception(exception, "warn", log_levels.WARN, request)

    @staticmethod
    def critical_error(exception: Exception, request: Request = None) -> None:
        log = Logger._get_base_log("critical_error", log_levels.CRITICAL, request)
        log["exc_info"] = traceback.format_exc()
        # Store last exception stack trace in request to obtain it in response
        Logger._register_last_exception(log["exc_info"], request)
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
        function: Callable, start: datetime, end: datetime, execution_time_ms: int
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
    def _get_base_log(log_type: str, level: str, request: Request = None) -> dict:
        base_log = {
            "project": ConfigProvider.get_env_var("PROJECT"),
            "version": ConfigProvider.get_env_var("PROJECT_VERSION"),
            "repository": ConfigProvider.get_env_var("PROJECT_REPOSITORY"),
            "environment": ConfigProvider.get_env_var("ENVIRONMENT"),
            "service": ConfigProvider.get_env_var("SERVICE"),
            "num_cpu_cores": hardware_metrics.get_available_cpu_count(),
            "type": log_type,
            "timestamp": Logger._get_timestamp(),
            "levelname": level,
            "data": {},
        }

        if request:
            base_log["request"] = Logger._get_request_info(request)

        return base_log

    @staticmethod
    def _get_request_info(request: Request) -> dict:
        return {
            "request_id": Logger._get_request_id(request),
            "user_id": Logger._get_user_id(request),
            "user_roles": Logger._get_user_role(request),
            "full_path": request.get_full_url(),
            "http_method": request.method,
            "content_type": request.content_type,
            "headers": Logger._clean_request_headers(dict(request.headers)),
        }

    @staticmethod
    def _get_user_id(request: Request) -> Optional[str]:
        if not hasattr(request, "authenticated_user") or not request.authenticated_user:
            return None
        return request.authenticated_user.user_id

    @staticmethod
    def _get_user_role(request: Request) -> Optional[str]:
        if (
            not hasattr(request, "authenticated_user")
            or not request.authenticated_user
            or not request.authenticated_user.role
        ):
            return None
        return request.authenticated_user.role.name

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
    def register_route_body_attributes_to_ignore(
        http_method: str, path: str, attrs_to_ignore: List[str]
    ) -> None:
        Logger._ROUTE_BODY_ATTRS_TO_IGNORE.append(
            {
                "http_method": http_method,
                "path": path,
                "attrs_to_ignore": attrs_to_ignore,
            }
        )

    @staticmethod
    def _get_request_body_attrs_to_ignore(request: Request) -> List[str]:
        base_attrs_to_ignore = ConfigProvider.get_logger_config()["requests"][
            "body_attrs_to_ignore"
        ]
        for route in Logger._ROUTE_BODY_ATTRS_TO_IGNORE:
            if route["http_method"].upper() == request.method.upper():
                return route["attrs_to_ignore"] + [
                    x for x in base_attrs_to_ignore if x not in route["attrs_to_ignore"]
                ]
        return base_attrs_to_ignore or []

    @staticmethod
    def _register_last_exception(exc_info: str, request: Request = None) -> None:
        if request:
            request.last_exc_info = exc_info

    @staticmethod
    def _get_request_id(request: Request) -> Optional[str]:
        request_id_header = ConfigProvider.get_env_var("REQUEST_ID_HEADER")
        if not request_id_header:
            return None
        headers = dict(request.headers)
        return headers.get(request_id_header)

    @staticmethod
    def _get_cleaned_request_body(request: Request) -> Optional[str]:
        if not hasattr(request, "_logging_body") or not request._logging_body:
            return None
        # If is json body
        try:
            raw_body = request._logging_body.decode("utf-8")
            json_body = json.loads(raw_body)
            cleaned_json = JSONCleaner.clean_json(
                json_body, Logger._get_request_body_attrs_to_ignore(request)
            )
            return json.dumps(cleaned_json)
        except Exception as e:
            Logger.error(e)
            return request._logging_body

    @staticmethod
    def _clean_request_headers(headers: dict) -> dict:
        _headers = deepcopy(headers)
        lowercase_headers_to_ignore = [
            x.lower()
            for x in ConfigProvider.get_logger_config()["requests"]["headers_to_ignore"]
        ]
        return {
            k: v
            for k, v in _headers.items()
            if k.lower() not in lowercase_headers_to_ignore
        }

    @staticmethod
    def _get_timestamp() -> str:
        return dates.to_utc_isostring(dates.now())

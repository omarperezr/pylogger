from copy import deepcopy
from distutils.util import strtobool
from typing import Callable

from django.http import HttpResponse
from logger import Logger
from rest_framework.request import Request

from config.config_provider import ConfigProvider
from utils import function_execution_timer


class LoggingMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self._log_request_bodies = strtobool(
            ConfigProvider.get_env_var("LOG_REQUEST_BODIES", str(False))
        )
        self._log_response_bodies = strtobool(
            ConfigProvider.get_env_var("LOG_RESPONSE_BODIES", str(False))
        )

    def __call__(self, request: Request) -> HttpResponse:
        try:
            if hasattr(request, "body"):
                request._logging_body = deepcopy(request.body)
            Logger.log_request(request, log_body=self._log_request_bodies)
            timed_result = function_execution_timer.execute_timed(
                self.get_response, request
            )
            Logger.log_response(
                timed_result["result"],
                timed_result["execution_time_ms"],
                request,
                log_body=self._log_response_bodies,
            )
        except Exception as e:
            Logger.critical_error(e, request)
            raise e
        return timed_result["result"]

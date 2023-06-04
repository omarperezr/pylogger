import json
import os
from datetime import timedelta

import pytest

from pylogger.logger import Logger, dates, function_execution_timer, loguru, traceback
from tests.mocks.mocked_request import MockedRequest
from tests.mocks.mocked_response import MockedResponse
from utils import hardware_metrics

last_log = None


def mocked_loguru_log(levelname: str, json_log: dict) -> None:
    global last_log
    last_log = {"levelname": levelname, "json_log": json.loads(json_log)}


@pytest.fixture(autouse=True)
def run_patches():
    os.environ["PROJECT"] = "Test project name"
    os.environ["PROJECT_VERSION"] = "0.1.0"
    os.environ["PROJECT_REPOSITORY"] = "test_project_repo"
    os.environ["ENVIRONMENT"] = "develop"
    os.environ["SERVICE"] = "test_service"
    os.environ["REQUEST_ID_HEADER"] = "request_id"

    original_functions = {
        "dates.now": dates.now,
        "hardware_metrics.get_available_cpu_count": hardware_metrics.get_available_cpu_count,
        "loguru.logger.log": loguru.logger.log,
        "function_execution_timer.execute_timed": function_execution_timer.execute_timed,
        "traceback.format_exc": traceback.format_exc,
    }

    # Patch
    dates.now = lambda: dates.to_datetime("2023-01-01 11:11:11")
    hardware_metrics.get_available_cpu_count = lambda: 3
    loguru.logger.log = mocked_loguru_log
    function_execution_timer.execute_timed = lambda function, *args, **kwargs: {
        "result": function(*args, **kwargs),
        "start_timestamp": dates.now(),
        "end_timestamp": dates.now() + timedelta(seconds=1),
        "execution_time_ms": 1000,
    }
    traceback.format_exc = lambda: "test stack trace"

    yield

    del os.environ["PROJECT"]
    del os.environ["PROJECT_VERSION"]
    del os.environ["PROJECT_REPOSITORY"]
    del os.environ["ENVIRONMENT"]
    del os.environ["SERVICE"]
    del os.environ["REQUEST_ID_HEADER"]

    # Recover
    dates.now = original_functions["dates.now"]
    hardware_metrics.get_available_cpu_count = original_functions[
        "hardware_metrics.get_available_cpu_count"
    ]
    loguru.logger.log = original_functions["loguru.logger.log"]
    function_execution_timer.execute_timed = original_functions[
        "function_execution_timer.execute_timed"
    ]
    traceback.format_exc = original_functions["traceback.format_exc"]


def test_log_request_removes_attrs_based_on_config():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"email":"test_user@test.com"}',
        "json",
        authenticated_user=None,
        headers={"request_id": "0123456789"},
    )
    Logger.log_request(request)
    assert last_log["levelname"] == "INFO"
    assert last_log["json_log"] == {
        "data": {"body": '{"email": "REMOVED"}'},
        "environment": "develop",
        "levelname": "INFO",
        "num_cpu_cores": 3,
        "project": "Test project name",
        "repository": "test_project_repo",
        "request": {
            "content_type": "json",
            "full_path": "/test/id?param=1",
            "headers": {"request_id": "0123456789"},
            "http_method": "POST",
            "request_id": "0123456789",
            "user_id": None,
            "user_roles": None,
        },
        "service": "test_service",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "type": "request",
        "version": "0.1.0",
    }


def test_log_request_logs_request_info():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        authenticated_user=None,
        headers={"request_id": "0123456789"},
    )
    Logger.log_request(request)
    assert last_log["levelname"] == "INFO"
    assert last_log["json_log"] == {
        "data": {"body": '{"key": "value"}'},
        "environment": "develop",
        "levelname": "INFO",
        "num_cpu_cores": 3,
        "project": "Test project name",
        "repository": "test_project_repo",
        "request": {
            "content_type": "json",
            "full_path": "/test/id?param=1",
            "headers": {"request_id": "0123456789"},
            "http_method": "POST",
            "request_id": "0123456789",
            "user_id": None,
            "user_roles": None,
        },
        "service": "test_service",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "type": "request",
        "version": "0.1.0",
    }


def test_log_response_logs_levelname_as_info_when_response_is_200():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        authenticated_user=None,
        headers={"request_id": "0123456789"},
    )
    response = MockedResponse(200, b'{"key":"value"}', {"Content-Type": "json"})
    Logger.log_response(response, 500, request)
    assert last_log["levelname"] == "INFO"
    assert last_log["json_log"] == {
        "data": {
            "body": '{"key":"value"}',
            "content_type": "json",
            "request_body": None,
            "status_code": 200,
        },
        "environment": "develop",
        "levelname": "INFO",
        "execution_time_ms": 500,
        "num_cpu_cores": 3,
        "project": "Test project name",
        "repository": "test_project_repo",
        "request": {
            "content_type": "json",
            "full_path": "/test/id?param=1",
            "headers": {"request_id": "0123456789"},
            "http_method": "POST",
            "request_id": "0123456789",
            "user_id": None,
            "user_roles": None,
        },
        "service": "test_service",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "type": "response",
        "version": "0.1.0",
    }


def test_log_response_logs_levelname_as_error_when_response_is_400():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        authenticated_user=None,
        headers={"request_id": "0123456789"},
    )
    response = MockedResponse(400, b'{"key":"value"}', {"Content-Type": "json"})
    Logger.log_response(response, 600, request)
    assert last_log["levelname"] == "ERROR"
    assert last_log["json_log"] == {
        "data": {
            "body": '{"key":"value"}',
            "content_type": "json",
            "request_body": '{"key": "value"}',
            "status_code": 400,
        },
        "environment": "develop",
        "exc_info": None,
        "levelname": "ERROR",
        "execution_time_ms": 600,
        "num_cpu_cores": 3,
        "project": "Test project name",
        "repository": "test_project_repo",
        "request": {
            "content_type": "json",
            "full_path": "/test/id?param=1",
            "headers": {"request_id": "0123456789"},
            "http_method": "POST",
            "request_id": "0123456789",
            "user_id": None,
            "user_roles": None,
        },
        "service": "test_service",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "type": "response",
        "version": "0.1.0",
    }


def test_critical_error_logs_exception():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        authenticated_user=None,
        headers={"request_id": "0123456789"},
    )
    Logger.critical_error(IndexError("Index error example"), request)
    assert last_log["levelname"] == "CRITICAL"
    assert last_log["json_log"] == {
        "data": {"exception_type": "IndexError"},
        "environment": "develop",
        "exc_info": "test stack trace",
        "levelname": "CRITICAL",
        "message": "Index error example",
        "num_cpu_cores": 3,
        "project": "Test project name",
        "repository": "test_project_repo",
        "request": {
            "content_type": "json",
            "full_path": "/test/id?param=1",
            "headers": {"request_id": "0123456789"},
            "http_method": "POST",
            "request_id": "0123456789",
            "user_id": None,
            "user_roles": None,
        },
        "service": "test_service",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "type": "critical_error",
        "version": "0.1.0",
    }


def test_get_request_info_sets_request_id_as_none_when_not_present():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        authenticated_user=None,
    )
    actual = Logger._get_request_info(request)
    assert actual == {
        "content_type": "json",
        "full_path": "/test/id?param=1",
        "headers": {},
        "http_method": "POST",
        "request_id": None,
        "user_id": None,
        "user_roles": None,
    }


def test_get_request_info_sets_user_id_none_when_no_user():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        headers={"request_id": "0123456789"},
    )
    actual = Logger._get_request_info(request)
    assert actual == {
        "content_type": "json",
        "full_path": "/test/id?param=1",
        "headers": {"request_id": "0123456789"},
        "http_method": "POST",
        "request_id": "0123456789",
        "user_id": None,
        "user_roles": None,
    }


def test_get_request_info_removes_auth_header():
    request = MockedRequest(
        "/test/id?param=1",
        "POST",
        b'{"key":"value"}',
        "json",
        headers={"User-Agent": "Test user agent", "Authorization": "Bearer 0123456789"},
    )
    actual = Logger._get_request_info(request)
    assert actual == {
        "content_type": "json",
        "full_path": "/test/id?param=1",
        "headers": {"User-Agent": "Test user agent"},
        "http_method": "POST",
        "request_id": None,
        "user_id": None,
        "user_roles": None,
    }

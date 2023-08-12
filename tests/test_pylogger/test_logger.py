import json
import os
from datetime import timedelta

import pytest

from pylogger.logger import Logger, dates, function_execution_timer, loguru, traceback
from utils import hardware_metrics

last_log = None


def mocked_loguru_log(levelname: str, json_log: dict) -> None:
    global last_log
    last_log = {"levelname": levelname, "json_log": json.loads(json_log)}


@pytest.fixture(autouse=True)
def run_patches():
    os.environ["PROJECT"] = "Logger"
    os.environ["PROJECT_VERSION"] = "0.1.0"
    os.environ["PROJECT_REPOSITORY"] = "test_project_repo"
    os.environ["ENVIRONMENT"] = "develop"
    os.environ["SERVICE"] = "test_service"

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


def test_log_execution_time_logs_correctly():
    @Logger.log_execution_time
    def func_to_be_timed():
        pass

    func_to_be_timed()
    assert last_log["levelname"] == "INFO"
    assert last_log["json_log"] == {
        "project": "Logger",
        "version": "0.1.0",
        "repository": "test_project_repo",
        "environment": "develop",
        "service": "test_service",
        "num_cpu_cores": 3,
        "type": "execution_time",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "levelname": "INFO",
        "data": {
            "start_timestamp": "2023-01-01T11:11:11+00:00",
            "end_timestamp": "2023-01-01T11:11:12+00:00",
            "module": "tests.test_pylogger.test_logger",
            "function": "func_to_be_timed",
            "full_name": "tests.test_pylogger.test_logger.func_to_be_timed",
        },
        "execution_time_ms": 1000,
    }


def test_log_info():
    Logger.info("test info message")
    assert last_log["levelname"] == "INFO"
    assert last_log["json_log"] == {
        "project": "Logger",
        "version": "0.1.0",
        "repository": "test_project_repo",
        "environment": "develop",
        "service": "test_service",
        "num_cpu_cores": 3,
        "type": "custom_message",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "levelname": "INFO",
        "data": {"extra_args": {}},
        "message": "test info message",
    }


def test_log_warn():
    mock_exception = Exception("test warn exception")
    Logger.warn(mock_exception)
    assert last_log["levelname"] == "WARN"
    assert last_log["json_log"] == {
        "project": "Logger",
        "version": "0.1.0",
        "repository": "test_project_repo",
        "environment": "develop",
        "service": "test_service",
        "num_cpu_cores": 3,
        "type": "warn",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "levelname": "WARN",
        "data": {"exception_type": "Exception"},
        "exc_info": "test stack trace",
        "message": "test warn exception",
    }


def test_log_error():
    mock_exception = Exception("test error exception")
    Logger.error(mock_exception)
    assert last_log["levelname"] == "ERROR"
    assert last_log["json_log"] == {
        "project": "Logger",
        "version": "0.1.0",
        "repository": "test_project_repo",
        "environment": "develop",
        "service": "test_service",
        "num_cpu_cores": 3,
        "type": "error",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "levelname": "ERROR",
        "data": {"exception_type": "Exception"},
        "exc_info": "test stack trace",
        "message": "test error exception",
    }


def test_log_critial_error():
    mock_exception = Exception("test critical error exception")
    Logger.critical_error(mock_exception)
    assert last_log["levelname"] == "CRITICAL"
    assert last_log["json_log"] == {
        "project": "Logger",
        "version": "0.1.0",
        "repository": "test_project_repo",
        "environment": "develop",
        "service": "test_service",
        "num_cpu_cores": 3,
        "type": "critical_error",
        "timestamp": "2023-01-01T11:11:11+00:00",
        "levelname": "CRITICAL",
        "data": {"exception_type": "Exception"},
        "exc_info": "test stack trace",
        "message": "test critical error exception",
    }

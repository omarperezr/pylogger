import time
from datetime import datetime
from typing import Any, Callable, Dict


def execute_timed(function: Callable, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Executes the given function with the provided arguments and returns a dictionary containing the start and end times,
    the execution time in milliseconds, and the result of the function.

    Args:
        function: The function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        A dictionary containing the start and end times, the execution time in milliseconds, and the result of the function.
    """
    start = time.perf_counter()
    result = function(*args, **kwargs)
    end = time.perf_counter()
    exec_time_ms = int((end - start) * 1000)
    return {
        "start_timestamp": datetime.fromtimestamp(start),
        "end_timestamp": datetime.fromtimestamp(end),
        "execution_time_ms": exec_time_ms,
        "result": result,
    }

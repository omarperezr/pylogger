[![Python package](https://github.com/omarperezr/pylogger/actions/workflows/python-package.yml/badge.svg)](https://github.com/omarperezr/pylogger/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# PyLogger
A Python library that provides a simple and efficient way to log messages and exceptions at different log levels. It uses the loguru library for logging, which is a powerful and flexible logging library that makes it easy to configure and customize your logging output.

With PyLogger, you can easily log custom messages at the INFO log level, as well as log exceptions at the ERROR, WARN, and CRITICAL log levels. You can also use the log_execution_time decorator to log the execution time of a function.

PyLogger comes with a variety of built-in handlers, including a file handler, a GCP handler, and a stdout handler. You can easily configure which handlers to use by modifying the handlers configuration in your PyLogger configuration file.

## Features
Simple and efficient logging of messages and exceptions at different log levels
Custom log levels
Built-in handlers for file, GCP, and stdout logging
Easy configuration of handlers through a configuration file
Log execution time of functions with the log_execution_time decorator
Installation
To install PyLogger, simply run the following command:

```py
pip install pylogger
```

Usage
To use PyLogger, simply import the Logger class and call its methods to log messages and exceptions at different log levels. Here's an example:

```py
from pylogger import Logger

# Log a custom message at the INFO log level
Logger.info("Custom message", {"extra_args": {"key": "value"}})

# Log an exception at the ERROR log level
try:
    # Some code that might raise an exception
    pass
except Exception as e:
    Logger.error(e)

# Log the execution time of a function
@Logger.log_execution_time
def my_function():
    # Function code here
    pass
```

# Configuration
PyLogger can be easily configured through a configuration file. By default, PyLogger looks for a configuration file named config.ini in the current working directory. Here's an example configuration file:

```ini
[Logger]
handlers = [
    "stdout",
    "gcp"
    ]
```

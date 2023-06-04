import json
import os
from typing import Any, Callable, Optional

from config.undefined import Undefined
from config.unset import Unset
from exceptions.env_var_not_set_exception import EnvVarNotSetException


class EnvVar:
    __UNDEFINED__ = Undefined()
    __UNSET__ = Unset()

    # We use __UNDEFINED__ for allowing to specify a default value of None
    def __init__(
        self,
        name: str,
        default_value: Any = __UNDEFINED__,
        value_formatter: Callable = lambda value: value,
        deserializer: Optional[str] = None,
    ) -> None:
        """
        The value of this config item is obtained from an environment variable.

        :param name: name of the environment variable to get
        :param default_value: value to use if the env var is not set (if not provided, it will raise an
            EnvVarNotSetException in case of the env var is not set)
        :param value_formatter: function used to format the value each time this is requested
        :param deserializer: function used to deserialize the env var content before the value_formatter is called, its
            value can be None or 'json', in case of None, no deserializer will be used (default value will also be
            deserialized)
        """
        self._name = name
        self._default = default_value
        self._value = EnvVar.__UNSET__
        self._value_formatter = value_formatter
        self._deserializer = deserializer
        if self._deserializer not in [None, "json"]:
            raise AssertionError(
                "Invalid deserializer. It must be one of: None, 'json'"
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_value(self) -> Any:
        return self._default

    @property
    def value(self) -> Any:
        # If the env var was never set or the last time it was checked it was not defined, we evaluate it
        if self._value in {EnvVar.__UNSET__, EnvVar.__UNDEFINED__}:
            value = os.environ.get(self.name, self.default_value)
            if self._deserializer == "json":
                self._value = json.loads(value)
            else:
                self._value = value
        # If the env var value was not found and there is no default configured value, we raise an exception
        if self._value == EnvVar.__UNDEFINED__:
            raise EnvVarNotSetException(f"{self.name} env var is not set")
        formatted_value = self._value_formatter(self._value)
        return formatted_value

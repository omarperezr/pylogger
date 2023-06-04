from typing import Any, Callable

from .unset import Unset


class DeferredInitConfig:
    __UNSET__ = Unset()

    def __init__(self, builder: Callable) -> None:
        """
        The value of this config item is calculated the first time it is called.
        It's useful when it's value is calculated from an environment variable that can not already be set at the moment
        of the declaration (like remotely obtained environment variables).

        :param builder: This parameter must be a function that returns the value of this config item
        """
        self._builder = builder
        self._value = DeferredInitConfig.__UNSET__

    @property
    def value(self) -> Any:
        if self._value == DeferredInitConfig.__UNSET__:
            self._value = self._builder()
        return self._value

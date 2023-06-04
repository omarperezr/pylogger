from typing import Any, Callable, Optional, Union

from config.deferred_init_config import DeferredInitConfig
from config.env_var import EnvVar


class BaseConfigProvider:
    """
    When extended by a class, it's required to expose it like a variable that is an instance of the class that is
    extending this one instead of the real class (this is because dunder class methods can not be overridden)
    For instance: If the child class is named ConfigProvider, after the class declaration it should be overridden like
    this: ConfigProvider = ConfigProvider()
    """

    ENVIRONMENT: str = EnvVar(
        "ENVIRONMENT", "local", value_formatter=lambda x: x.lower()
    )
    PROJECT: str = EnvVar("PROJECT")

    def __getattribute__(self, attr_name: str) -> Any:
        attr = getattr(self, attr_name)
        dispatch = {EnvVar: lambda x: x.value, DeferredInitConfig: lambda x: x.value}
        return dispatch.get(type(attr), lambda x: x)(attr)

    @staticmethod
    def config(
        source: Union[Callable, str],
        default_value: Any = EnvVar.__UNDEFINED__,
        value_formatter: Callable = lambda value: value,
        deserializer: Optional[str] = None,
    ) -> Union[EnvVar, DeferredInitConfig]:
        """
        :param source: If source is a function, a DeferredInitConfig is initialized. If source is a string, an EnvVar is
            initialized
        :param default_value: Only used in case of environment variables. Refers to EnvVar default_value.
        :param value_formatter: Only used in case of environment variables. Refers to EnvVar value_formatter.
        :param deserializer: Only used in case of environment variables. Refers to EnvVar deserializer. It can be None
            or 'json'
        """
        if callable(source):
            return DeferredInitConfig(source)
        if isinstance(source, str):
            return EnvVar(
                source,
                default_value=default_value,
                value_formatter=value_formatter,
                deserializer=deserializer,
            )
        raise NotImplementedError(
            f"A mapping for type {type(source)} is not implemented"
        )


# These methods are exposed here to allow them to be used directly without having call BaseConfigProvider first
config = BaseConfigProvider.config

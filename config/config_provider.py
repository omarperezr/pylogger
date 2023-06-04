import os
from pathlib import Path
from typing import Any, Callable, Union

import yaml

from config.base_config_provider import BaseConfigProvider
from exceptions.config_not_found_exception import ConfigNotFoundException


class ConfigProvider(BaseConfigProvider):
    _CONFIG_FILE_NAME_TEMPLATE = "{0}_config.yml"
    _CONFIG_FILES_DIR_NAME = "config_files"

    _loaded_configs = {}
    _cached_configs = {}

    @staticmethod
    def _get_class_config(
        config_files_path: str, category: str, class_type: Union[type, str]
    ):
        ConfigProvider._try_load_config(config_files_path, category)
        class_name = class_type.__name__ if isinstance(class_type, type) else class_type
        try:
            return ConfigProvider._loaded_configs[category][class_name]
        except KeyError:
            raise ConfigNotFoundException(f"There is not a config for '{class_name}'")

    @staticmethod
    def get_env_var(env_var_name: str, default: Any = None) -> Any:
        return os.environ.get(env_var_name, default)

    @staticmethod
    def recover_or_obtain(key: str, data_obtain_function: Callable) -> Any:
        """
        If key value is cached in cached configs, it's value is retrieved. Else, data_obtain_function
        is called and returned value is stored for provided key and retrieved
        """
        if key not in ConfigProvider._cached_configs:
            ConfigProvider._cached_configs[key] = data_obtain_function()
        return ConfigProvider._cached_configs[key]

    @staticmethod
    def remove_cached(key: str):
        """
        Removes the provided config key from the cache
        """
        if key in ConfigProvider._cached_configs:
            del ConfigProvider._cached_configs[key]

    @staticmethod
    def _try_load_config(config_files_path: str, config_name: str) -> None:
        if config_name in ConfigProvider._loaded_configs:
            return
        ConfigProvider._load_config(config_files_path, config_name)

    @staticmethod
    def _load_config(config_files_path: str, config_name: str) -> None:
        config_filename = ConfigProvider._CONFIG_FILE_NAME_TEMPLATE.format(config_name)

        config_path = (
            Path(config_files_path)
            / ConfigProvider._CONFIG_FILES_DIR_NAME
            / config_filename
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                ConfigProvider._loaded_configs[config_name] = yaml.safe_load(f)
        except OSError:
            raise ConfigNotFoundException(
                f"Config file '{config_filename}' could not be found"
            )

    @staticmethod
    def get_logger_config() -> dict:
        ConfigProvider._try_load_config(
            os.path.dirname(os.path.abspath(__file__)), "logger"
        )
        return ConfigProvider._loaded_configs["logger"]

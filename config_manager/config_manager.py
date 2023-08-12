import configparser
from typing import List, Tuple


class ConfigManager:
    def __init__(self, config_file_path: str = "config/config.ini"):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    def save(self) -> None:
        with open(self.config_file_path, "w") as config_file:
            self.config.write(config_file)

    def has_section(self, section) -> bool:
        return self.config.has_section(section)

    def has_option(self, section, option) -> bool:
        return self.config.has_option(section, option)

    def get(self, section, key) -> str:
        return self.config.get(section, key)

    def get_sections(self) -> List[str]:
        return self.config.sections()

    def get_options(self, section) -> List[str]:
        return self.config.options(section)

    def get_items(self, section) -> List[Tuple[str, str]]:
        return self.config.items(section)

    def set_config(self, section, key, value) -> None:
        self.config.set(section, key, value)

    def set_section(self, section) -> None:
        self.config.add_section(section)

    def remove_section(self, section) -> None:
        self.config.remove_section(section)

    def remove_option(self, section, option) -> None:
        self.config.remove_option(section, option)


config_manager = ConfigManager()

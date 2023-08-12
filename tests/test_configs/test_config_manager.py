import configparser

import pytest

from config_manager.config_manager import ConfigManager


class TestConfigManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.config_manager = ConfigManager("config/test_config.ini")

    # Tests that ConfigManager can read and parse a valid config file
    def test_read_valid_config_file(self):
        assert self.config_manager.get_sections() == ["Section1", "Section2"]
        assert self.config_manager.get_options("Section1") == ["option1", "option2"]
        assert self.config_manager.get("Section1", "option1") == "value1"
        assert self.config_manager.get("Section2", "option3") == "value3"

    # Tests that ConfigManager can save changes to the config file
    def test_save_changes_to_config_file(self, mocker):
        mock_file = mocker.patch(
            "builtins.open", mocker.mock_open(read_data="mocked data")
        )
        self.config_manager.save()
        mock_file.assert_called_with("config/test_config.ini", "w")
        mock_file().write.assert_called_with(mocker.ANY)

    # Tests that ConfigManager can retrieve a value from a section and key
    def test_retrieve_value_from_section_and_key(self):
        assert self.config_manager.get("Section1", "option1") == "value1"

    # Tests that ConfigManager can add a new section to the config file
    def test_add_new_section_to_config_file(self):
        self.config_manager.set_section("Section3")
        assert self.config_manager.get_sections() == [
            "Section1",
            "Section2",
            "Section3",
        ]

    # Tests that ConfigManager can remove a section from the config file
    def test_remove_section_from_config_file(self):
        self.config_manager.remove_section("Section1")
        assert self.config_manager.get_sections() == ["Section2"]

    # Tests that ConfigManager can remove an option from a section
    def test_remove_option_from_section(self):
        self.config_manager.remove_option("Section1", "option1")
        assert self.config_manager.get_options("Section1") == ["option2"]

    # Tests that ConfigManager returns False when checking for a non-existent section
    def test_non_existent_section_returns_false(self):
        assert self.config_manager.has_section("non_existent_section") == False

    # Tests that ConfigManager returns False when checking for a non-existent option
    def test_non_existent_option_returns_false(self):
        assert (
            self.config_manager.has_option("Section1", "non_existent_option") == False
        )

    # Tests that ConfigManager raises an error when attempting to retrieve a non-existent section or key
    def test_retrieve_non_existent_section_or_key_raises_error(self):
        with pytest.raises(configparser.NoSectionError):
            self.config_manager.get("non_existent_section", "option1")
        with pytest.raises(configparser.NoOptionError):
            self.config_manager.get("Section1", "non_existent_option")

    # Tests that ConfigManager raises an error when attempting to set a value for a non-existent section or key
    def test_set_value_for_non_existent_section_raises_error(self):
        with pytest.raises(configparser.NoSectionError):
            self.config_manager.set_config("non_existent_section", "option1", "value1")

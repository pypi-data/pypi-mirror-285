import logging
from contextlib import suppress
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QSettings

SETTINGS = None


class _Settings:
    def __init__(self, settings_path: Path, default_settings_dictionary: dict):
        self.settings_path = settings_path
        self.default_settings_dictionary = default_settings_dictionary

        self.settings = QSettings(str(self.settings_path), QSettings.Format.IniFormat)

        logging.getLogger("Settings").debug(f"Settings path: {self.settings_path}")

    def _parse_enum(self, setting_type, setting):
        setting_value = self.settings.value(setting)

        if isinstance(setting_value, str):
            with suppress(ValueError):
                return setting_type(setting_value)

        return self.default_settings_dictionary[setting]

    @staticmethod
    def _get_storage_value(setting_value):
        if isinstance(setting_value, Enum):
            return setting_value.value

        if isinstance(setting_value, (Path, str)):
            return str(setting_value)

        return setting_value

    def get(self, setting: str):
        setting_type = type(self.default_settings_dictionary[setting])

        if issubclass(setting_type, Enum):
            return self._parse_enum(setting_type, setting)

        return self.settings.value(setting, self.default_settings_dictionary[setting], type=setting_type)

    def set(self, setting_name: str, setting_value):
        setting_type = type(self.default_settings_dictionary[setting_name])

        if setting_type != type(setting_value):
            raise ValueError(f"Setting {setting_name} is of type {setting_type} but value is of type {type(setting_value)}.")

        setting_value = self._get_storage_value(setting_value)

        self.settings.setValue(setting_name, setting_value)

    def reset(self, setting_name):
        self.set(setting_name, self.default_settings_dictionary[setting_name])

    def get_all(self) -> dict:
        return {k: self.get(k) for k in self.default_settings_dictionary}

    def sync(self):
        self.settings.sync()

    def sync_get(self, setting):
        self.sync()
        return self.get(setting)

    @property
    def filename(self):
        return self.settings.fileName()


def Settings(settings_path: Path, default_settings_dictionary: dict):
    global SETTINGS

    if not SETTINGS:
        SETTINGS = _Settings(settings_path, default_settings_dictionary)

    return SETTINGS

"""Configuration module for QuClo."""

import configparser
from typing import Dict
from quclo.utils import CONFIG_FILE


class Config:
    """A configuration"""

    @staticmethod
    def _save_key_value(section: str, key: str, value: str):
        """Save a key value pair to the configuration file."""
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        if section not in config:
            config[section] = {}
        config[section][key] = value
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

    @staticmethod
    def _load_key_value(section: str, key: str) -> str:
        """Load a key value pair from the configuration file."""
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config[section][key]

    @staticmethod
    def save_api_key(api_key: str):
        """Save the API key to the configuration file."""
        Config._save_key_value("auth", "api_key", api_key)

    @staticmethod
    def load_api_key() -> str:
        """Load the API key from the configuration file."""
        return Config._load_key_value("auth", "api_key")

    @staticmethod
    def save_default_user(email: str):
        """Save the default user to the configuration file."""
        Config._save_key_value("user", "email", email)

    @staticmethod
    def load_default_user() -> str:
        """Load the default user from the configuration file."""
        email = Config._load_key_value("user", "email")
        return email

    @staticmethod
    def save_default_backend(backend: str):
        """Save the default backend to the configuration file."""
        Config._save_key_value("backend", "name", backend)

    @staticmethod
    def load_default_backend() -> str:
        """Load the default backend from the configuration file."""
        return Config._load_key_value("backend", "name")

    @staticmethod
    def save_default_priority(priority: str):
        """Save the default priority to the configuration file."""
        Config._save_key_value("priority", "value", priority)

    @staticmethod
    def load_default_priority() -> str:
        """Load the default priority from the configuration file."""
        return Config._load_key_value("priority", "value")

    @staticmethod
    def save_config(data: Dict[str, Dict[str, str]]):
        """Save the configuration to the configuration file."""
        config = configparser.ConfigParser()
        for section, values in data.items():
            config[section] = values
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
